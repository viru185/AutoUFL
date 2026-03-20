"""
Excel to CSV transformation logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
from typing import Dict, Iterable

import pandas as pd
from loguru import logger

from src.config import ISO_TIMESTAMP_FORMAT, MONTH_FORMATS, SHEET_NAME
from src.mapping import TAG_MAPPING

MONTH_CANDIDATE_PATTERN = re.compile(r"^[A-Za-z]{3,9}[-\s]\d{2,4}$")


class ProcessingError(Exception):
    """Raised when the workbook cannot be transformed."""


@dataclass
class ProcessResult:
    output_file: Path
    rows_written: int


class ExcelProcessor:
    """Handles ingesting Excel files and emitting normalized CSV rows."""

    def __init__(
        self,
        sheet_name: str = SHEET_NAME,
        tag_mapping: Dict[str, str] | None = None,
    ) -> None:
        self.sheet_name = sheet_name
        self.tag_mapping = tag_mapping or TAG_MAPPING
        self._normalized_tag_mapping = {
            self._clean_text(name): tag for name, tag in self.tag_mapping.items()
        }
        self._warned_descriptions: set[str] = set()

    def process_file(self, file_path: Path, output_dir: Path) -> ProcessResult:
        """Transform an Excel workbook into a normalized CSV."""
        file_path = file_path.resolve()
        output_dir = output_dir.resolve()

        logger.info(f"Processing file '{file_path}'")

        df = self._read_sheet(file_path)
        normalized = self._normalize(df)

        if normalized.empty:
            raise ProcessingError("No data rows were produced after normalization.")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self._unique_output_path(output_dir / f"{file_path.stem}.csv")
        logger.info(f"Writing normalized CSV to '{output_path}'")
        try:
            normalized.to_csv(output_path, index=False)
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"Failed to write CSV output for '{output_path}'")
            raise ProcessingError(f"Failed to write CSV for '{output_path.name}'.") from exc

        logger.info(
            f"Processing successful for '{file_path.name}' -> {len(normalized)} rows into {output_path}",
        )
        return ProcessResult(output_file=output_path, rows_written=len(normalized))

    # ------------------------------------------------------------------ helpers
    def _read_sheet(self, file_path: Path) -> pd.DataFrame:
        logger.info(f"Reading Excel file '{file_path}' (sheet '{self.sheet_name}')")
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=self.sheet_name,
                dtype=object,
            )
        except ValueError as exc:
            logger.exception(
                f"Invalid Excel format: sheet '{self.sheet_name}' not found in '{file_path}'",
            )
            raise ProcessingError(f"Invalid Excel format: Sheet '{self.sheet_name}' is missing.") from exc
        except FileNotFoundError as exc:
            logger.exception(f"File not found: {file_path}")
            raise ProcessingError(f"File not found: {file_path}") from exc
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"Failed to read Excel workbook '{file_path}'")
            raise ProcessingError(f"Failed to read Excel workbook '{file_path.name}'.") from exc

        df = df.dropna(how="all")  # drop empty rows
        if df.empty:
            raise ProcessingError(f"Sheet '{self.sheet_name}' in {file_path} is empty.")
        logger.debug(f"Exact column names: {list(df.columns)}")
        return df

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Normalizing worksheet data")
        df = df.copy()
        df = self._promote_header_row_if_needed(df)
        df.columns = self._normalize_headers(df.columns)
        logger.debug(f"Columns found: {df.columns.tolist()}")

        desc_col, uom_col = self._validate_structure(df)

        df = df.rename(columns={desc_col: "Description", uom_col: "UOM"})
        df["Description"] = df["Description"].map(self._clean_text)
        df["UOM"] = df["UOM"].map(self._clean_text)

        logger.debug(f"Sample data:\n{df.head().to_string(index=False)}")

        logger.info("Dropping FY column(s)")
        df = self._drop_fy_columns(df)

        logger.info("Parsing dates")
        month_columns = self._extract_month_columns(df.columns)

        logger.info("Melting dataframe")
        melted = df.melt(
            id_vars=["Description", "UOM"],
            value_vars=list(month_columns.keys()),
            var_name="Month",
            value_name="Value",
        )

        melted = melted.dropna(subset=["Value", "Description", "UOM"])
        melted["Value"] = melted["Value"].map(self._clean_value)
        melted = melted[melted["Value"] != ""]
        melted["Description"] = melted["Description"].map(self._clean_text)
        melted["UOM"] = melted["UOM"].map(self._clean_text)

        logger.info("Mapping tags")
        melted["Tag"] = melted["Description"].map(self._map_description_to_tag)
        missing_tags = sorted(
            {desc for desc in melted.loc[melted["Tag"].isna(), "Description"] if desc}
        )
        if missing_tags:
            logger.debug(f"Unmapped descriptions: {missing_tags}")
        melted = melted.dropna(subset=["Tag"])

        if melted.empty:
            return melted

        melted["MonthDate"] = melted["Month"].map(month_columns.get)
        melted["DateTime"] = melted["MonthDate"].map(lambda dt: dt.strftime(ISO_TIMESTAMP_FORMAT))

        melted = self._duplicate_march_rows(melted)

        ordered = melted[["Tag", "DateTime", "Description", "Value", "UOM"]]
        return ordered.reset_index(drop=True)

    def _validate_structure(self, df: pd.DataFrame) -> tuple[str, str]:
        logger.info("Validating input structure")
        normalized = {self._clean_text(col).lower(): col for col in df.columns}
        missing = [col for col in ("description", "uom") if col not in normalized]
        if missing:
            message = "Invalid Excel format: Missing required columns: " + ", ".join(col.title() for col in missing)
            logger.error(message)
            raise ProcessingError(message)
        return normalized["description"], normalized["uom"]

    @classmethod
    def _normalize_headers(cls, columns: Iterable[object]) -> list[str]:
        return [cls._normalize_single_header(col) for col in columns]

    @classmethod
    def _normalize_single_header(cls, value: object) -> str:
        dt_candidate = cls._coerce_header_datetime(value)
        if dt_candidate:
            return dt_candidate.strftime("%b-%y")

        text = cls._clean_text(value)
        if not text:
            return ""

        dt_from_text = cls._parse_header_text_to_datetime(text)
        if dt_from_text:
            return dt_from_text.strftime("%b-%y")

        return text

    @staticmethod
    def _coerce_header_datetime(value: object) -> datetime | None:
        if isinstance(value, pd.Timestamp):
            dt_value = value.to_pydatetime()
        elif isinstance(value, datetime):
            dt_value = value
        elif isinstance(value, date):
            dt_value = datetime.combine(value, datetime.min.time())
        else:
            return None
        return dt_value.replace(day=1)

    @staticmethod
    def _parse_header_text_to_datetime(text: str) -> datetime | None:
        cleaned = text.replace("–", "-").replace("—", "-")
        for fmt in MONTH_FORMATS:
            try:
                return datetime.strptime(cleaned, fmt).replace(day=1)
            except ValueError:
                continue

        if any(sep in cleaned for sep in ("-", "/", " ")):
            try:
                parsed = pd.to_datetime(cleaned, errors="raise")
            except Exception:
                return None
            if isinstance(parsed, pd.Timestamp):
                parsed = parsed.to_pydatetime()
            if isinstance(parsed, datetime):
                return parsed.replace(day=1)
        return None

    def _promote_header_row_if_needed(self, df: pd.DataFrame) -> pd.DataFrame:
        normalized_columns = self._normalize_headers(df.columns)
        if self._has_required_headers(normalized_columns):
            df = df.copy()
            df.columns = normalized_columns
            return df

        logger.info("Searching for header row within worksheet data")
        max_scan_rows = min(len(df), 50)
        for idx in range(max_scan_rows):
            row_values = self._normalize_headers(df.iloc[idx].tolist())
            if self._has_required_headers(row_values):
                logger.info(f"Promoting row {idx} to header row")
                logger.debug(f"Promoted header values: {row_values}")
                trimmed = df.iloc[idx + 1 :].reset_index(drop=True)
                trimmed.columns = row_values
                return trimmed

        logger.warning("Failed to auto-detect header row; continuing with original columns")
        df = df.copy()
        df.columns = normalized_columns
        return df

    @staticmethod
    def _has_required_headers(headers: Iterable[str]) -> bool:
        normalized = {header.lower() for header in headers}
        return "description" in normalized and "uom" in normalized

    def _drop_fy_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        fy_columns = [col for col in df.columns if self._clean_text(col).lower().startswith("fy")]
        if fy_columns:
            logger.debug(f"FY columns removed: {fy_columns}")
            return df.drop(columns=fy_columns)
        logger.debug("No FY columns detected during normalization")
        return df

    def _extract_month_columns(self, columns: Iterable[str]) -> Dict[str, datetime]:
        month_map: Dict[str, datetime] = {}
        for col in columns:
            if col in {"Description", "UOM"}:
                continue
            normalized = self._clean_text(col)
            if normalized.lower().startswith("fy"):
                continue

            if not self._looks_like_month_label(normalized):
                logger.debug(f"Skipping non-month column '{normalized}'.")
                continue

            parsed = self._parse_month_label(normalized, original_label=col)
            month_map[col] = parsed

        if not month_map:
            raise ProcessingError("No month columns detected in the worksheet.")

        return month_map

    def _parse_month_label(self, label: str, *, original_label: str) -> datetime:
        """Attempt to parse a month label like 'Apr-25' into a datetime."""
        cleaned = self._normalize_month_label(label)
        for fmt in MONTH_FORMATS:
            try:
                dt = datetime.strptime(cleaned, fmt)
                return dt.replace(day=1)
            except ValueError:
                continue

        try:
            parsed = pd.to_datetime(cleaned, format="%b-%y", errors="raise")
            if isinstance(parsed, pd.Timestamp):
                return parsed.to_pydatetime().replace(day=1)
            return parsed.replace(day=1)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Date parsing failed for '{original_label}'")
            raise ProcessingError(f"Date parsing failed for '{original_label}'.") from exc

    def _duplicate_march_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        march_mask = df["MonthDate"].dt.month == 3
        if not march_mask.any():
            return df.drop(columns=["MonthDate"], errors="ignore")

        march_rows = df.loc[march_mask].copy()
        df.loc[march_mask, "DateTime"] = df.loc[march_mask, "MonthDate"].map(
            lambda dt: dt.replace(day=1).strftime(ISO_TIMESTAMP_FORMAT)
        )
        march_rows["DateTime"] = march_rows["MonthDate"].map(lambda dt: dt.replace(day=31).strftime(ISO_TIMESTAMP_FORMAT))

        combined = pd.concat([df, march_rows], ignore_index=True)
        return combined.drop(columns=["MonthDate"], errors="ignore")

    def _map_description_to_tag(self, description: str) -> str | None:
        normalized_description = self._clean_text(description)
        tag = self._normalized_tag_mapping.get(normalized_description)
        if tag:
            return tag

        if normalized_description and normalized_description not in self._warned_descriptions:
            logger.warning(f"No PI tag mapping for description '{normalized_description}'.")
            self._warned_descriptions.add(normalized_description)
        return None

    @staticmethod
    def _clean_text(value: object) -> str:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        text = str(value).strip()
        text = text.replace("–", "-").replace("—", "-")
        return " ".join(text.split())

    @staticmethod
    def _clean_value(value: object) -> str:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        text = str(value).strip()
        return text

    @staticmethod
    def _normalize_month_label(label: str) -> str:
        return " ".join(label.replace("–", "-").replace("—", "-").split()).strip()

    @staticmethod
    def _looks_like_month_label(label: str) -> bool:
        return bool(MONTH_CANDIDATE_PATTERN.match(label.lower()))

    @staticmethod
    def _unique_output_path(path: Path) -> Path:
        candidate = path
        counter = 1
        while candidate.exists():
            candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
            counter += 1
        if candidate != path:
            logger.info(f"Output file exists, using '{candidate.name}' instead")
        return candidate
