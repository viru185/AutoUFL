import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import DEFAULT_TIMESTAMP, TAG_FILE
from src.logger import logger


class ProcessingError(Exception):
    """
    Raised when the workbook cannot be Processed.
    """


@dataclass
class ProcessResult:
    """
    A dataclass representing the result of a file processing operation.
    """

    output_file: Path
    rows_written: int


class baseExcelProcessor:
    """
    Base class for processing Excel files.
    """

    @staticmethod
    def _drop_columns_by_regex(df: pd.DataFrame, patterns: list[str]) -> pd.DataFrame:
        """
        Drops columns whose names match any of the given regex patterns.

        Args:
            df (pd.DataFrame): Input dataframe
            patterns (list[str]): List of regex patterns

        Returns:
            pd.DataFrame: Cleaned dataframe
        """

        compiled_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

        cols_to_drop = []

        for col in df.columns:
            col_str = str(col)  # ensure it's string

            for pattern in compiled_patterns:
                if pattern.search(col_str):
                    cols_to_drop.append(col)
                    break  # no need to check other patterns

        return df.drop(columns=cols_to_drop, errors="ignore")

    @staticmethod
    def _set_header(df, threshold=10) -> pd.DataFrame:
        """
        Set the header of a DataFrame based on a threshold of datetime objects.
        args:
            df (pd.DataFrame): The DataFrame to set the header for.
            threshold (int): The minimum number of datetime objects in a row to consider it a header.

        returns:
            pd.DataFrame: The DataFrame with the header set.
        """

        # Drop empty rows and reset index WITHOUT adding an 'index' column
        df = df.dropna(how="all").reset_index(drop=True)

        for index, row in df.iterrows():
            # Count datetime objects in the current row
            datetime_count = sum(isinstance(val, (pd.Timestamp, datetime)) for val in row)

            if datetime_count > threshold:
                # Set the current row as the new header
                # row.values ensures we aren't carrying over any Series metadata
                df.columns = row.values

                # Slice from the NEXT row to the end
                df = df.iloc[index + 1 :].copy()

                # Clean up formatting
                df.columns.name = None

                return df.reset_index(drop=True)

        raise ProcessingError("No valid month header found")

    @staticmethod
    def _map_description_to_tag(df: pd.DataFrame, mapping: dict, tag_file: Path = TAG_FILE) -> pd.DataFrame:
        """
        Maps values from 'Description' to 'Tag' using a dictionary + JSON file.

        - Loads mapping from JSON file (if exists and readable)
        - File mapping takes priority over provided mapping
        - New mappings are added to file mapping
        - Updates JSON file with latest mapping

        args:
            df (pd.DataFrame): Input DataFrame
            mapping (dict): New mapping dictionary
            tag_file (Path): Path to JSON mapping file

        returns:
            pd.DataFrame: Updated DataFrame
        """

        if "Description" not in df.columns:
            raise ValueError("Column 'Description' not found in DataFrame")

        # Ensure Tag column exists
        df["Tag"] = df.get("Tag", None)

        # Clean Description
        df["Description"] = df["Description"].astype(str).str.strip()

        file_mapping = {}

        # Load JSON file safely
        if tag_file.exists() and tag_file.is_file():
            try:
                with open(tag_file, "r", encoding="utf-8") as f:
                    file_mapping = json.load(f)
            except Exception:
                logger.error(f"Error loading JSON file: {tag_file}")
                file_mapping = {}

        # Merge mappings
        # Priority: file_mapping > mapping
        merged_mapping = mapping.copy()

        # overwrite with file mapping (file wins)
        merged_mapping.update(file_mapping)

        # add new keys from mapping into file_mapping (for persistence)
        file_mapping.update(mapping)

        # Apply mapping
        df["Tag"] = df["Description"].map(merged_mapping).fillna(df["Tag"])

        # Save updated mapping back to file
        try:
            tag_file.parent.mkdir(parents=True, exist_ok=True)
            with open(tag_file, "w", encoding="utf-8") as f:
                json.dump(file_mapping, f, indent=4, ensure_ascii=False)
        except Exception:
            logger.exception(f"Error saving JSON file: {tag_file}")

        return df

    @staticmethod
    def _prepare_ufl_csv_df(df: pd.DataFrame, time_of_day: str = DEFAULT_TIMESTAMP) -> pd.DataFrame:
        """
        Convert a wide month-based dataframe into UFL CSV format.

        Input columns expected:
            Tag, Description, UOM, and month columns

        Output columns:
            Tag, DateTime, Description, Value, UOM

        Rules:
        - Month headers are normalized to the 1st day of the month
        - DateTime uses the supplied time_of_day (example: "05:00:00")
        - March gets two rows per record:
            1) start of month
            2) end of month
        - Commas are removed from Description

        args:
            df (pd.DataFrame): The DataFrame to prepare.
            time_of_day (str): The time of day to use for the DateTime column.

        returns:
            pd.DataFrame: A DataFrame in UFL CSV format.
        """

        df = df.copy()

        # Ensure required columns exist
        for col in ["Tag", "Description", "UOM"]:
            if col not in df.columns:
                df[col] = None

        # Clean Description
        df["Description"] = df["Description"].astype("string").str.replace(",", "", regex=False).str.strip()

        id_vars = ["Tag", "Description", "UOM"]
        month_cols = [c for c in df.columns if c not in id_vars]

        def _normalize_month(col) -> pd.Timestamp:
            parsed = pd.to_datetime(col, errors="coerce")

            if pd.isna(parsed):
                parsed = pd.to_datetime(str(col), format="%b-%y", errors="coerce")

            if pd.isna(parsed):
                parsed = pd.to_datetime(str(col), errors="coerce")

            if pd.isna(parsed):
                raise ValueError(f"Cannot parse month header: {col!r}")

            return parsed.to_period("M").to_timestamp()

        # Map month headers to normalized month-start timestamps
        month_map = {col: _normalize_month(col) for col in month_cols}

        # Wide -> long
        out = df.melt(
            id_vars=id_vars,
            value_vars=month_cols,
            var_name="Month",
            value_name="Value",
        )

        # Remove empty values
        out = out.dropna(subset=["Value"]).copy()

        # Build base datetime = first day of month + supplied time
        time_delta = pd.to_timedelta(time_of_day)
        out["MonthStart"] = out["Month"].map(month_map)
        out["DateTime"] = out["MonthStart"] + time_delta

        # Add March end-of-month rows
        march_rows = out[out["MonthStart"].dt.month == 3].copy()
        if not march_rows.empty:
            march_rows["DateTime"] = march_rows["MonthStart"] + pd.offsets.MonthEnd(0) + time_delta
            out = pd.concat([out, march_rows], ignore_index=True)

        # Format DateTime exactly for CSV output
        out["DateTime"] = pd.to_datetime(out["DateTime"]).dt.strftime("%Y-%m-%dT%H:%M:%S")

        # Final output layout
        out = out[["Tag", "DateTime", "Description", "Value", "UOM"]]

        # round to 4 decimal places
        out["Value"] = out["Value"].round(4)

        return out.reset_index(drop=True)

    @staticmethod
    def _get_output_file_path(file_path: Path, output_dir: Path) -> Path:
        """
        Generate a unique CSV file path.
        Always ensures .csv extension.

        args:
            file_path (Path): The path to the input file.
            output_dir (Path): The path to the output directory.

        returns:
            Path: The unique CSV file path.
        """

        # Force .csv extension FIRST
        stem = file_path.stem
        output_file = output_dir / f"{stem}.csv"

        # If file doesn't exist → return immediately
        if not output_file.exists():
            return output_file

        counter = 1

        while True:
            new_name = f"{stem}_{counter}.csv"
            output_file = output_dir / new_name

            if not output_file.exists():
                return output_file

            counter += 1

    @staticmethod
    def _rename_columns(df: pd.DataFrame, column_map: dict):
        """
        Rename dataframe columns using a mapping dictionary.

        Args:
            df (pd.DataFrame): Input dataframe
            column_map (dict): Mapping of old column names to new names

        Returns:
            pd.DataFrame: DataFrame with renamed columns
        """
        if df is None or df.empty:
            return df

        # Only rename columns that actually exist in df
        valid_map = {k: v for k, v in column_map.items() if k in df.columns}
        logger.debug(f"Renaming columns: {valid_map}")

        return df.rename(columns=valid_map)

    @staticmethod
    def _get_sheet_name(file_path: Path, sheets_to_process_regex: list[str]):
        """
        Get sheet names from an Excel file with regex matching.

        args:
            file_path (Path): The path to the Excel file.
            sheets_to_process_regex (list[str]): A list of regex patterns to match sheet names.

        returns:
            list[str]: A list of matching sheet names.
        """
        try:
            excel = pd.ExcelFile(file_path)
            sheet_names = [str(s) for s in excel.sheet_names]

            # Compile all patterns
            patterns = [re.compile(p, re.IGNORECASE) for p in sheets_to_process_regex]

            # Match if ANY pattern matches
            matched_sheets = [sheet for sheet in sheet_names if any(p.match(sheet) for p in patterns)]

            return matched_sheets

        except Exception as e:
            logger.error(f"Failed to get sheet names from {file_path}: {e}")
            return []

    @classmethod
    def _save_ufl_csv(cls, df: pd.DataFrame, file_path: Path, output_dir: Path) -> Path:
        """
        Save the DataFrame to a CSV file.

        args:
            df (pd.DataFrame): The DataFrame to be saved.
            file_path (Path): The path to the input file.
            output_dir (Path): The path to the output directory.

        returns:
            bool: True if the file was saved successfully, False otherwise.
        """
        try:
            _output_file = cls._get_output_file_path(file_path, output_dir)
            df.to_csv(_output_file, index=False, header=True, float_format="%.4f")
            logger.debug(f"file saved: {_output_file}")
            return _output_file
        except:
            logger.exception(f"Error saving file: {file_path}")
            return Path()
