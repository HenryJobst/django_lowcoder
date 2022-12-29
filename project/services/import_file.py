from pathlib import Path

from pandas import DataFrame

from project.models import TransformationFile, Model
from project.services.importer import Importer


def import_file(
    importer: Importer, sheet_params: dict[str, Importer.SheetReaderParams] = None
) -> dict[str, DataFrame]:
    result = {}
    for sheet in importer.sheets():
        sheet_reader_parameters: Importer.SheetReaderParams = (
            Importer.SheetReaderParams()
        )
        if sheet_params and sheet in sheet_params:
            sheet_reader_parameters = sheet_params[sheet]
        df: DataFrame = importer.run(
            sheet_name=sheet, sheet_reader_params=sheet_reader_parameters
        )
        result.update({sheet: (df, sheet_reader_parameters)})
    return True, result
