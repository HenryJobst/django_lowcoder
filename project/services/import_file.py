from django.template.defaultfilters import slugify
from pandas import DataFrame

from project.services.importer import Importer, SheetReaderParams


def import_file(
    importer: Importer, sheet_params: dict[str, SheetReaderParams] = None
) -> tuple[bool, dict[str, tuple[DataFrame, SheetReaderParams]]]:
    result = {}
    for sheet in importer.sheets():
        slugified_sheet = slugify(sheet)
        sheet_reader_parameters: SheetReaderParams = SheetReaderParams()
        if sheet_params and slugified_sheet in sheet_params:
            sheet_reader_parameters = sheet_params[slugified_sheet]
        try:
            df: DataFrame = importer.run(
                sheet_name=sheet, sheet_reader_params=sheet_reader_parameters
            )
        except ValueError as e:
            df = DataFrame(data={"Fehler": [e]})
        result.update({sheet: (df, sheet_reader_parameters)})
    return True, result
