from pathlib import Path

from project.services.importer import (
    Importer,
    SheetReaderParams,
    DEFAULT_SHEET_NAME_FOR_CSV_FILE,
)


class TestImport:
    project = "project/tests"

    def test_sample_csv(self, pytestconfig):
        path = pytestconfig.rootpath.joinpath(
            Path("project/tests/sample_files/Employee-Sample-Data.csv")
        )
        importer = Importer(path)
        sheet0 = DEFAULT_SHEET_NAME_FOR_CSV_FILE
        df = importer.run(sheet0, SheetReaderParams())
        assert not df.empty

    def test_sample_xlsx(self, pytestconfig):
        path = pytestconfig.rootpath.joinpath(
            Path("project/tests/sample_files/Employee-Sample-Data.xlsx")
        )
        importer = Importer(path)
        sheet0 = importer.sheets()[0]
        df = importer.run(sheet0, SheetReaderParams())
        assert not df.empty

    def test_sample_multisheet_xlsx(self, pytestconfig):
        path = pytestconfig.rootpath.joinpath(
            Path("project/tests/sample_files/Testtabelle.xlsx")
        )
        importer = Importer(path)
        sheet0 = importer.sheets()[0]
        df = importer.run(sheet0, SheetReaderParams())
        assert not df.empty
