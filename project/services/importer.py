from pathlib import Path

import pandas as pd
from django.template.defaultfilters import slugify
from pandas import ExcelFile, DataFrame


class Importer:
    class SheetReaderParams:
        def __init__(self):
            self.header = 0
            self.usecols = None
            self.index_col = None
            self.skiprows = None
            self.nrows = None
            self.skipfooter = 0

    def __init__(
        self,
        filepath: Path,
    ):
        self.filepath: Path = filepath
        self.is_csv = self.filepath.suffix == ".csv"
        if not self.is_csv:
            self.xlsx: ExcelFile = pd.ExcelFile(self.filepath)

    def sheets(self) -> list[str]:
        if self.is_csv:
            return ["sheet0"]
        else:
            return self.xlsx.sheet_names

    def run(
        self,
        sheet_name: str,
        sheet_reader_params: SheetReaderParams = SheetReaderParams(),
    ) -> DataFrame:
        if self.is_csv:
            df = pd.read_csv(
                self.filepath,
                engine="python",
                sep=None,  # automatic detection
                encoding_errors="replace",
            )
        else:
            df = pd.read_excel(
                self.xlsx,
                sheet_name=sheet_name,
                header=sheet_reader_params.header,
                usecols=sheet_reader_params.usecols,
                index_col=sheet_reader_params.index_col,
                skiprows=sheet_reader_params.skiprows,
                nrows=sheet_reader_params.nrows,
                skipfooter=sheet_reader_params.skipfooter,
                dtype=object,  # no conversion
                decimal=",",  # use "," as decimal point
            )

        return df

    # noinspection PyMethodMayBeStatic
    def handle_dataframe(self, sheet_name, dataframe):
        dataframe.rename(
            columns={
                column: slugify(column).replace("-", "_")
                for column in dataframe.columns
            },
            inplace=True,
        )

        print()
        print("---")
        print(sheet_name)
        print(dataframe.head())
