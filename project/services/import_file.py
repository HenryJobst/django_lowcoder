from pathlib import Path

from pandas import DataFrame

from project.models import TransformationFile, Model
from project.services.importer import Importer


def import_file(file: Path, sheet_params=None) -> dict[str, DataFrame]:
    importer = Importer(file)
    sheets = importer.sheets()
    result = {}
    for sheet in sheets:
        sheet_reader_parameters = None
        if sheet_params and sheet in sheet_params:
            sheet_reader_parameters = sheet_params[sheet]
        df = importer.run(sheet_name=sheet, sheet_reader_params=sheet_reader_parameters)
        result.update({sheet: (df, sheet_reader_parameters)})
    return result
