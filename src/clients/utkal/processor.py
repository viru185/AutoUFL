from pathlib import Path

import pandas as pd

from src.clients.base_processor import ProcessingError, ProcessResult, baseExcelProcessor
from src.logger import logger

from .client_config import COLUMNS_TO_DRIP_RE_EXPRESSION, SHEETS_TO_PROCESS, TAG_MAPPING, COLUMN_RENAME_MAP


class ExcelProcessor(baseExcelProcessor):
    """Handles ingesting Excel files and emitting normalized CSV rows."""

    def __init__(
        self,
    ) -> None:
        self.sheet_names: list[str] = SHEETS_TO_PROCESS

        # clean mapping keys
        self.tag_mapping: dict[str, str] = {str(k).strip(): v for k, v in TAG_MAPPING.items()}

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

    def process_file(self, file_path: Path, output_dir: Path) -> ProcessResult:  # type: ignore
        try:
            # load the Excel file
            df = pd.read_excel(file_path, header=None)

            # set the header dynamically
            df = self._set_header(df)

            # drop columns by regex
            df = self._drop_columns_by_regex(df, COLUMNS_TO_DRIP_RE_EXPRESSION)

            # rename columns
            df = self._rename_columns(df, COLUMN_RENAME_MAP)

            # map description to tag
            df = self._map_description_to_tag(df, self.tag_mapping)

            # clean the dataframe
            df = self._clean_df(df)

            # Only drops rows where the 'Tag' column is None
            logger.info(f"Dropping rows where the 'Tag' column is None, count: {df['Tag'].isnull().sum()}")
            df = df.dropna(subset=['Tag'])

            # prepare the dataframe for UFL CSV format
            df = self._prepare_ufl_csv_df(df)

            output_file_path = self._save_ufl_csv(df, file_path, output_dir)

            return ProcessResult(rows_written=df.shape[0], output_file=output_file_path)

        except Exception:
            logger.exception(f"Processing failed: {file_path.name}")
