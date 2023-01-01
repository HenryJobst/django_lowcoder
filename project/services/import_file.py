from typing import Dict, Tuple

from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from pandas import DataFrame

from project.services.importer import Importer, SheetReaderParams


def import_file(
    importer: Importer, sheet_params: Dict[str | int, SheetReaderParams]
) -> Tuple[bool, Dict[str | int, Tuple[DataFrame, SheetReaderParams]]]:
    result: Dict[str | int, Tuple[DataFrame, SheetReaderParams]] = {}
    sheet: str | int
    for sheet in importer.sheets():
        slugified_sheet: str | int
        if isinstance(sheet, str):
            slugified_sheet = slugify(sheet)
        else:
            slugified_sheet = sheet

        sheet_reader_parameters: SheetReaderParams = SheetReaderParams()
        if sheet_params and slugified_sheet in sheet_params:
            sheet_reader_parameters = sheet_params[slugified_sheet]
        try:
            df: DataFrame = importer.run(
                sheet=sheet, sheet_reader_params=sheet_reader_parameters
            )
        except ValueError as e:
            df = DataFrame(data={_("Fehler"): [e]})
        result.update({sheet: (df, sheet_reader_parameters)})
    return True, result
