from datetime import datetime
from pathlib import Path

import pandas as pd

from src.clients.base_processor import ProcessResult, baseExcelProcessor
from src.logger import logger

from .client_config import COLUMN_RENAME_MAP, COLUMNS_TO_DROP_RE_EXPRESSION, SHEETS_TO_PROCESS, TAG_MAPPING


class ExcelProcessor(baseExcelProcessor):
    """Handles ingesting Excel files and emitting normalized CSV rows."""

    def __init__(
        self,
    ) -> None:
        self.sheet_names: list[str] = SHEETS_TO_PROCESS

        # clean mapping keys
        self.tag_mapping: dict[str, str] = {str(k).strip(): v for k, v in TAG_MAPPING.items()}

        # month mapping
        self.month_map = {
            "JAN": 1,
            "FEB": 2,
            "MAR": 3,
            "APR": 4,
            "MAY": 5,
            "JUN": 6,
            "JUL": 7,
            "AUG": 8,
            "SEP": 9,
            "OCT": 10,
            "NOV": 11,
            "DEC": 12,
        }

    @staticmethod
    def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Client specific cleaning

        args:
            df (pd.DataFrame): The DataFrame to clean

        returns:
            pd.DataFrame: The cleaned DataFrame
        """

        return df

    def _convert_months_to_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert month names to dates

        args:
            df (pd.DataFrame): The DataFrame to clean

        returns:
            pd.DataFrame: The cleaned DataFrame
        """
        current_year = datetime.now().year
        new_cols = []

        for col in df.columns:
            col_clean = str(col).strip().upper()

            if col_clean in self.month_map:
                month = self.month_map[col_clean]

                # FY logic (Apr–Mar)
                year = current_year if month >= 4 else current_year + 1

                date = pd.Timestamp(year=year, month=month, day=1)
                new_cols.append(date)
            else:
                new_cols.append(col)

        df.columns = new_cols
        return df

    def process_file(self, file_path: Path, output_dir: Path) -> ProcessResult:  # type: ignore
        try:
            # load the Excel file
            df = pd.read_excel(file_path, sheet_name="Production Plan", header=1)

            # drop columns by regex
            df = self._drop_columns_by_regex(df, COLUMNS_TO_DROP_RE_EXPRESSION)

            # rename columns
            df = self._rename_columns(df, COLUMN_RENAME_MAP)

            # map description to tag
            df = self._map_description_to_tag(df, self.tag_mapping)

            # clean the dataframe
            # df = self._clean_df(df)

            # convert month names to dates
            df = self._convert_months_to_dates(df)

            # Only drops rows where the 'Tag' column is None
            logger.info(f"Dropping rows where the 'Tag' column is None, count: {df['Tag'].isnull().sum()}")
            df = df.dropna(subset=["Tag"])

            # prepare the dataframe for UFL CSV format
            df = self._prepare_ufl_csv_df(df)

            output_file_path = self._save_ufl_csv(df, file_path, output_dir)

            return ProcessResult(rows_written=df.shape[0], output_file=output_file_path)

        except Exception:
            logger.exception(f"Processing failed: {file_path.name}")
