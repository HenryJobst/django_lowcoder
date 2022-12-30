from pathlib import Path

from project.services.importer import Importer, SheetReaderParams


class TestImport:
    def test_sample_csv(self):
        importer = Importer(Path("./sample_files/Employee-Sample-Data.csv"))
        sheet0 = "sheet0"
        df = importer.run(sheet0, SheetReaderParams())
        assert not df.empty

    def test_sample_xlsx(self):
        importer = Importer(Path("./sample_files/Employee-Sample-Data.xlsx"))
        sheet0 = importer.sheets()[0]
        df = importer.run(sheet0, SheetReaderParams())
        assert not df.empty

    def test_sample_multisheet_xlsx(self):
        importer = Importer(Path("./sample_files/Testtabelle.xlsx"))
        sheet0 = importer.sheets()[0]
        df = importer.run(sheet0, SheetReaderParams())
        assert not df.empty
