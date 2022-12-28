from pathlib import Path

from project.models import TransformationFile, Model
from project.services.importer import Importer


def import_file(file: TransformationFile) -> (bool, list[Model]):
    importer = Importer(Path(file))
    importer.run()
    return True, []
