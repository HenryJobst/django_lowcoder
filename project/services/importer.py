from pathlib import Path
from typing import Sequence, Callable, Any, Optional

import pandas as pd
from django.contrib import messages
from django.http import HttpRequest
from django.template.defaultfilters import slugify
from pandas import ExcelFile, DataFrame

from project.models import (
    TransformationFile,
    TransformationMapping,
    TransformationSheet,
    TransformationHeadline,
    TransformationColumn,
    Model,
    Field,
)

DEFAULT_SHEET_NAME_FOR_CSV_FILE = "sheet0"

READ_PARAM_HEADER = "header"
READ_PARAM_INDEX_COL = "index_col"
READ_PARAM_NROWS = "nrows"
READ_PARAM_SKIPFOOTER = "skipfooter"
READ_PARAM_SKIPROWS = "skiprows"
READ_PARAM_USECOLS = "usecols"

TABLE_PARAM_HEAD_ROWS = "head_rows"
TABLE_PARAM_TAIL_ROWS = "tail_rows"
DEFAULT_HEAD_TAIL_ROWS = 5


def convert_param(param: str, value: Optional[Any]) -> int | str | None:
    if param == READ_PARAM_HEADER:
        return int(value) if value else 0
    elif param == READ_PARAM_USECOLS:
        return str(value) if value and value != "" else None
    elif param == READ_PARAM_SKIPROWS:
        return int(value) if value else None
    elif param == READ_PARAM_NROWS:
        return int(value) if value else None
    elif param == READ_PARAM_SKIPFOOTER:
        return int(value) if value else 0
    elif param == TABLE_PARAM_HEAD_ROWS:
        return int(value) if value else DEFAULT_HEAD_TAIL_ROWS
    elif param == TABLE_PARAM_TAIL_ROWS:
        return int(value) if value else DEFAULT_HEAD_TAIL_ROWS

    return None


class SheetReaderParams(dict):
    def __init__(
        self,
        header: int | Sequence[int] | None = 0,
        usecols: int
        | str
        | Sequence[int]
        | Sequence[str]
        | Callable[[str], bool]
        | None = None,
        index_col: int | Sequence[int] | None = None,
        skiprows: Sequence[int] | int | Callable[[int], object] | None = None,
        nrows: int | None = None,
        skipfooter: int = 0,
        head_rows: int = DEFAULT_HEAD_TAIL_ROWS,
        tail_rows: int = DEFAULT_HEAD_TAIL_ROWS,
    ):
        dict.__init__(
            self,
            header=header,
            usecols=usecols,
            index_col=index_col,
            skiprows=skiprows,
            nrows=nrows,
            skipfooter=skipfooter,
            head_rows=head_rows,
            tail_rows=tail_rows,
        )


def create_models(
    request: HttpRequest,
    file: TransformationFile,
    df_by_sheet: dict[str, tuple[DataFrame, SheetReaderParams]],
    clean_existing_models: bool,
):

    tm: TransformationMapping = file.transformation_mapping

    if clean_existing_models:
        pass
    #     tm.files.sheets.all().delete()
    #     tm.models.all().delete()
    else:
        #     file.sheets.headlines.models.all().delete()
        file.sheets.all().delete()

    index = -1
    for item in df_by_sheet.items():
        index += 1
        sheet = item[0]
        df_tuple = item[1]

        # tm.models.filter(name=slugified_sheet).delete()

        df: DataFrame = df_tuple[0]
        settings = df_tuple[1]

        ts, created = TransformationSheet.objects.get_or_create(
            transformation_file=file, index=index + 1
        )

        header_offset = settings.get(READ_PARAM_HEADER)
        skiprows = settings.get(READ_PARAM_SKIPROWS)
        skiprows = skiprows if skiprows else 0

        th, created = TransformationHeadline.objects.get_or_create(
            transformation_sheet=ts, row_index=header_offset + skiprows
        )

        # Model.objects.filter(transformation_mapping=tm, index=index).delete()
        model, created = Model.objects.update_or_create(
            transformation_mapping=tm,
            index=index + 1,
            defaults={
                "transformation_headline": th,
                "name": sheet,
                "is_main_entity": index == 0,
            },
        )

        if created:
            messages.info(request, f"Die Tabelle: {model.name} wurde angelegt.")
        else:
            messages.info(request, f"Die Tabelle: {model.name} wurde aktualisiert.")

        for col_index, col in enumerate(df.columns):
            tc, created = TransformationColumn.objects.get_or_create(
                transformation_headline=th, column_index=col_index
            )

            field, created = Field.objects.update_or_create(
                model=model,
                index=col_index + 1,
                defaults={
                    "name": col,
                    "transformation_column": tc,
                    "datatype": Field.DATATYPES[4][0],
                },
            )

            if created:
                messages.info(request, f"Die Spalte: {field.name} wurde angelegt.")
            else:
                messages.info(request, f"Die Spalte: {field.name} wurde aktualisiert.")


class Importer:
    def __init__(self, filepath: Path):
        self.filepath: Path = filepath
        self.is_csv = self.filepath.suffix == ".csv"
        if not self.is_csv:
            self.xlsx: ExcelFile = pd.ExcelFile(self.filepath)

    def sheets(self) -> list[int | str]:
        if self.is_csv:
            return [DEFAULT_SHEET_NAME_FOR_CSV_FILE]
        else:
            return self.xlsx.sheet_names

    def run(
        self,
        sheet_name: str,
        sheet_reader_params: SheetReaderParams,
    ) -> DataFrame:
        if self.is_csv:
            df = pd.read_csv(
                self.filepath,
                engine="python",
                sep=None,  # automatic detection
                encoding_errors="replace",
            )
        else:
            df = pd.read_excel(  # type: ignore
                self.xlsx,
                sheet_name=sheet_name,
                header=sheet_reader_params.get(READ_PARAM_HEADER),
                usecols=sheet_reader_params.get(READ_PARAM_USECOLS),
                index_col=sheet_reader_params.get(READ_PARAM_INDEX_COL),
                skiprows=sheet_reader_params.get(READ_PARAM_SKIPROWS),
                nrows=sheet_reader_params.get(READ_PARAM_NROWS),
                skipfooter=convert_param(
                    READ_PARAM_SKIPFOOTER,
                    sheet_reader_params.get(READ_PARAM_SKIPFOOTER),
                ),  # type: ignore
                dtype=object,
                # no conversion
                decimal=",",
                # use "," as decimal point
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
