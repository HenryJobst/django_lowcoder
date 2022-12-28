from pathlib import Path
from pprint import pprint

import pandas as pd
from django.template.defaultfilters import slugify


class Importer:
    def __init__(self, filepath: Path):
        self.filepath: Path = filepath
        self.is_csv = self.filepath.suffix == ".csv"

    def run(self) -> bool:
        if self.is_csv:
            df = pd.read_csv(self.filepath)
        else:
            df = pd.read_excel(self.filepath, dtype=object)

        df.rename(
            columns={
                column: slugify(column).replace("-", "_") for column in df.columns
            },
            inplace=True,
        )

        pprint(df.head())

        return True
