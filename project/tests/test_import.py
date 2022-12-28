from pathlib import Path

from project.services.importer import Importer


class TestImport:
    def test_sample_csv(self):
        importer = Importer(Path("./sample_files/Employee-Sample-Data.csv"))
        assert importer.run()

    def test_sample_xlsx(self):
        importer = Importer(Path("./sample_files/Employee-Sample-Data.xlsx"))
        assert importer.run()

