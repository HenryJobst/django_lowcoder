from pathlib import Path

import pytest
from pandas import Series, DataFrame

from project.models import Field
from project.services.import_field import ImportField
from project.services.importer import Importer, SheetReaderParams


class TestImportField:
    project = "project/tests"

    def test_choices(self, pytestconfig):
        path = pytestconfig.rootpath.joinpath(
            Path("project/tests/sample_files/Employee-Sample-Data.xlsx")
        )
        df: DataFrame = df_of_file(path)

        department_series: Series = df[df.columns[3]]
        import_field = ImportField(department_series)

        assert import_field.field_type == Field.Datatype.INTEGER_FIELD
        assert len(import_field.choices) == 7

    @pytest.mark.parametrize("dtype", ["object", "string"])
    def test_string_choices(self, dtype):
        series: Series = Series(["a", "b", "c", "a", "a", "c", "c"], dtype=dtype)

        import_field = ImportField(series)

        assert import_field.field_type == Field.Datatype.INTEGER_FIELD
        assert len(import_field.choices) == 3

    @pytest.mark.parametrize("dtype", ["object", "string"])
    def test_unique_from_min_data_size(self, dtype):
        series: Series = Series(["a", "b", "c"], dtype=dtype)

        import_field = ImportField(series)

        assert import_field.field_type == Field.Datatype.CHAR_FIELD
        assert not import_field.propose_unique()


def df_of_file(path) -> DataFrame:
    importer = Importer(path)
    sheet0 = importer.sheets()[0]
    return importer.run(sheet0, SheetReaderParams())
