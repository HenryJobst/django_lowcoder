from pathlib import Path

from project.services.model_exporter import ModelExporter


class ModelExporterJpa(ModelExporter):
    def export(self) -> Path | None:
        return None
