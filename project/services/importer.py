import datetime
from pathlib import Path
from typing import Sequence, Callable, Any, Optional, List, Tuple, Dict, Final

import pandas as pd
from django.contrib import messages
from django.http import HttpRequest
from django.template.defaultfilters import slugify
from pandas import ExcelFile, DataFrame, Timestamp

from project.models import (
    TransformationFile,
    TransformationMapping,
    TransformationSheet,
    TransformationHeadline,
    TransformationColumn,
    Model,
    Field,
)
from project.services.import_field import ImportField
import pytz

DEFAULT_SHEET_NAME_FOR_CSV_FILE = "sheet0"

READ_PARAM_HEADER = "header"
READ_PARAM_INDEX_COL = "index_col"
READ_PARAM_NROWS = "nrows"
READ_PARAM_SKIPFOOTER = "skipfooter"
READ_PARAM_SKIPROWS = "skiprows"
READ_PARAM_USECOLS = "usecols"
TIMEZONE_PARAM = "timezone"

TABLE_PARAM_HEAD_ROWS = "head_rows"
TABLE_PARAM_TAIL_ROWS = "tail_rows"
DEFAULT_HEAD_TAIL_ROWS = 5
DEFAULT_TIMEZONE = "Europe/Berlin"


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
        timezone: str = DEFAULT_TIMEZONE,
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
            timezone=timezone,
        )


def fixture(model_name: str, df: DataFrame, timezone: str):
    df_as_dict = df.to_dict(orient="records")
    local_tz = pytz.timezone(timezone)
    target_tz = pytz.timezone("UTC")
    patched_df = []
    for record in df_as_dict:
        patched_dict = {}
        for k, v in record.items():
            if str(v).lower() == "nan":
                patched_dict[k] = None
            else:
                patched_dict[k] = convert_to_utc_str(v, local_tz, target_tz)

        patched_df.append(patched_dict)

    return [
        {
            "model": f"{model_name}",
            "pk": i,
            "fields": {
                k: None if str(v).lower() == "nan" else v for k, v in fields.items()
            },
        }
        for i, fields in enumerate(patched_df, start=1)
    ]


def convert_to_utc_str(value, local_tz, target_tz) -> str:
    # convert date, time and datetime to string,
    # otherwise it is not serializable
    if isinstance(value, Timestamp):
        local_dt = local_tz.localize(value)
        utc_dt = target_tz.normalize(local_dt)
        return utc_dt.isoformat()
    return value


def create_models(
    request: HttpRequest,
    file: TransformationFile,
    df_by_sheet: Dict[str | int, Tuple[DataFrame, SheetReaderParams]],
    clean_existing_models: bool,
):

    kwarg_fields: Final[List[str]] = [
        ImportField.CHOICES,
        ImportField.MAX_DIGITS,
        ImportField.MAX_LENGTH,
        ImportField.DECIMAL_PLACES,
        ImportField.BLANK,
        ImportField.NULL,
    ]

    tm: TransformationMapping = file.transformation_mapping

    if clean_existing_models:
        pass
    #     tm.files.sheets.all().delete()
    #     tm.models.all().delete()
    else:
        #     file.sheets.headlines.models.all().delete()
        file.sheets.all().delete()

    item: Tuple[str | int, Tuple[DataFrame, SheetReaderParams]]
    for index, item in enumerate(df_by_sheet.items()):
        sheet: str | int = item[0]
        df_tuple: Tuple[DataFrame, SheetReaderParams] = item[1]

        # tm.models.filter(name=slugified_sheet).delete()

        df: DataFrame = df_tuple[0]
        settings: SheetReaderParams = df_tuple[1]

        ts, created = TransformationSheet.objects.get_or_create(
            transformation_file=file, index=index + 1
        )

        header_offset: int = settings.get(READ_PARAM_HEADER, 0)
        skiprows: int = settings.get(READ_PARAM_SKIPROWS, 0)
        skiprows = skiprows if skiprows else 0

        content = fixture(sheet, df, settings.get(TIMEZONE_PARAM))
        th, created = TransformationHeadline.objects.get_or_create(
            transformation_sheet=ts,
            row_index=header_offset + skiprows,
            defaults={"content": content},
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

            import_field = ImportField(df[col])

            tc, created = TransformationColumn.objects.get_or_create(
                transformation_headline=th,
                column_index=col_index,
                defaults={"name": import_field.field_name},
            )

            defaults = {
                "name": col,
                "transformation_column": tc,
                "datatype": import_field.field_type
                if import_field.field_type
                else None,
                "is_unique": not import_field.has_duplicate_values,
                "default_value": None,
            }

            defaults.update(
                {
                    k: import_field.kwargs.get(k)
                    for k in kwarg_fields
                    if k in import_field.kwargs
                }
            )

            Field.objects.update_or_create(
                model=model,
                index=col_index + 1,
                defaults=defaults,
            )


class Importer:
    def __init__(self, filepath: Path):
        self.filepath: Path = filepath
        self.is_csv = self.filepath.suffix == ".csv"
        if not self.is_csv:
            self.xlsx: ExcelFile = pd.ExcelFile(self.filepath)

    def sheets(self) -> List[int | str]:
        if self.is_csv:
            return [DEFAULT_SHEET_NAME_FOR_CSV_FILE]
        else:
            return self.xlsx.sheet_names

    def run(
        self,
        sheet: str | int,
        sheet_reader_params: SheetReaderParams,
    ) -> DataFrame:
        if self.is_csv:
            df = pd.read_csv(
                self.filepath,
                engine="python",
                sep=None,  # automatic detection
                encoding_errors="replace",
                header=sheet_reader_params.get(READ_PARAM_HEADER),
                usecols=sheet_reader_params.get(READ_PARAM_USECOLS),
                index_col=sheet_reader_params.get(READ_PARAM_INDEX_COL),
                skiprows=sheet_reader_params.get(READ_PARAM_SKIPROWS),
                nrows=sheet_reader_params.get(READ_PARAM_NROWS),
                skipfooter=convert_param(
                    READ_PARAM_SKIPFOOTER,
                    sheet_reader_params.get(READ_PARAM_SKIPFOOTER),
                ),  # type: ignore
                decimal=",",
                # use "," as decimal point
                on_bad_lines="warn",
            )
        else:
            df = pd.read_excel(  # type: ignore
                self.xlsx,
                sheet_name=sheet,
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
