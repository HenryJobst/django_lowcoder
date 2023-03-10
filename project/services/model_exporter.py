from pathlib import Path

from project.services.cookiecutter_template_expander import CookieCutterTemplateExpander


class ModelExporter:
    def __init__(self, cte: CookieCutterTemplateExpander):
        self.cookieCutterTemplateExpander = cte

    def export(self) -> Path | None:
        raise RuntimeError(
            "ModelExporter.export isn't available. Please subclass the ModelExporter class!"
        )
