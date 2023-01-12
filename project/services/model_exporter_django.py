from datetime import datetime
from pathlib import Path

from django.db.models import QuerySet
from django.utils.text import slugify

from project.models import Model, Field
from project.services.model_exporter import ModelExporter

APP_NAME = "core"


class FieldTransform:
    def __init__(self, field: Field):
        self.field: Field = field

    def to_model_dot_py(self):
        return f"\r\t{slugify(self.field.name).replace('-', '_')} = {self.field_type_and_kwargs()}"

    def field_type_and_kwargs(self) -> str:
        kwargs = {}
        field_type = (
            f"models.{Field.DATATYPE_LABEL_BY_VALUE[self.field.datatype]}({{}})"
        )
        if self.field.max_length:
            kwargs["max_length"] = self.field.max_length
        if self.field.max_digits:
            kwargs["max_digits"] = self.field.max_digits
        if self.field.decimal_places:
            kwargs["decimal_places"] = self.field.decimal_places
        if self.field.null:
            kwargs["null"] = self.field.null
        if self.field.blank:
            kwargs["blank"] = self.field.blank
        if self.field.index:
            kwargs["index"] = self.field.index
        if self.field.is_unique:
            kwargs["unique"] = self.field.is_unique
        if self.field.choices and len(self.field.choices) > 1:
            kwargs["choices"] = self.field.choices

        kwargs_expanded = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        return field_type.format(kwargs_expanded)


class ModelTransform:
    def __init__(self, model: Model):
        self.model: Model = model

    def to_model_dot_py(self) -> str:
        s = f"class {slugify(self.model.name).replace('-', '')}(models.Model):\r\t"
        field: Field
        for field in self.model.fields.all():
            if field.exclude:
                continue
            s += FieldTransform(field).to_model_dot_py()

        s += "\r\r\t"
        s += "__str__ = __repr__ = lambda self: f'{self.id}'"

        s += f"\r\r\t"
        s += "def __str__(self):"
        s += "\r\t\treturn f'{self.id}'"

        return s


class ModelExporterDjango(ModelExporter):
    def export(self):
        app_dir: Path = self.create_app_dir()
        self.create_model_py(app_dir)
        self.create_admin_py()
        self.create_views_py()

    def create_app_dir(self) -> Path:
        app_dir = Path(
            self.cookieCutterTemplateExpander.expand_parameter.output_dir, APP_NAME
        )
        app_dir.mkdir(exist_ok=True, parents=True)
        return app_dir

    def create_model_py(self, app_dir: Path):

        models_py = app_dir.joinpath("models.py")

        output = f"# Created by Django LowCoder at {datetime.now()}\r\r"
        output += "from django.db import models\r\r"

        # noinspection PyUnresolvedReferences
        models: QuerySet[
            Model
        ] = self.cookieCutterTemplateExpander.project.transformationmapping.models
        model: Model
        for model in models.all():
            if model.exclude:
                continue
            output += "\r\r" + ModelTransform(model).to_model_dot_py()

        models_py.write_text(output)

    def create_admin_py(self):
        pass

    def create_views_py(self):
        pass
