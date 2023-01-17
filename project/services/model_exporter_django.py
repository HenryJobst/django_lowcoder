import json
import string
from datetime import datetime
from pathlib import Path

from black import Mode, TargetVersion, format_file_in_place, WriteBack
from django.db.models import QuerySet
from django.utils.text import slugify

from project.models import Model, Field
from project.services.cookiecutter_template_expander import CookieCutterTemplateExpander
from project.services.model_exporter import ModelExporter

MAX_DROPDOWN_SIZE = 20


def to_classname(name):
    return string.capwords(slugify(name).replace("-", " ")).replace(" ", "")


def to_varname(name):
    return slugify(name).replace("-", "_")


def text_to_default(datatype: int, default_value: str):
    if datatype == Field.Datatype.INTEGER_FIELD:
        return int(default_value)
    elif datatype == Field.Datatype.DECIMAL_FIELD:
        return replace_decimal_sign(default_value)

    return default_value


def replace_decimal_sign(value: str):
    new_value = ""
    sign = False
    for ch in reversed(value):
        if not sign and ch == ",":
            new_value += "."
            sign = True
            continue
        elif ch == ".":
            sign = True

        new_value = ch + new_value


class FieldTransform:
    def __init__(self, field: Field):
        self.field: Field = field

    def to_model_dot_py(self):
        return f"\r    {to_varname(self.field.name)} = {self.field_type_and_kwargs()}"

    def to_admin_dot_py_fields(self) -> str | None:
        if not self.field.show_in_detail:
            return None
        return f"'{to_varname(self.field.name)}'"

    def to_admin_dot_py_search_fields(self) -> str | None:
        if not self.field.use_index:
            return None
        return f"'{to_varname(self.field.name)}'"

    def to_admin_dot_py_list_display(self) -> str | None:
        if not self.field.show_in_list:
            return None
        return f"'{to_varname(self.field.name)}'"

    def to_admin_dot_py_list_filter(self) -> str | None:
        if self.field.is_unique:
            return None
        return f"'{to_varname(self.field.name)}'"

    def to_admin_dot_py_date_hierarchy(self) -> str | None:
        if (
            self.field.datatype != Field.Datatype.DATE_FIELD
            and self.field.datatype != Field.Datatype.DATE_TIME_FIELD
        ):
            return None
        return f"'{to_varname(self.field.name)}'"

    def to_admin_dot_py_autocomplete_fields(self) -> str | None:
        if (
            not self.field.foreign_key_entity
            or self.field.foreign_key_entity.fields.count() > MAX_DROPDOWN_SIZE
        ):
            return None
        return f"'{to_varname(self.field.name)}'"

    def field_type_and_kwargs(self) -> str:
        kwargs = {}
        field_type = f"models.{Field.DATATYPE_LABEL_BY_VALUE[self.field.datatype]}(_('{self.field.name}'), {{}})"
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
        if self.field.use_index:
            kwargs["db_index"] = True
        if self.field.is_unique:
            kwargs["unique"] = self.field.is_unique
        if self.field.choices and len(self.field.choices) > 1:
            choices = ", ".join(
                f"({k}, _('{v}'))" for k, v in self.field.choices.items()
            )
            kwargs["choices"] = f"[{choices}]"
        if self.field.description:
            kwargs["help_text"] = self.field.description
        if self.field.default_value:
            kwargs["default"] = text_to_default(
                self.field.datatype,
                self.field.default_value,
            )

        kwargs_expanded = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        return field_type.format(kwargs_expanded)


class ModelTransform:
    def __init__(self, model: Model):
        self.model: Model = model

    def to_model_dot_py(self) -> str:
        s = f"class {to_classname(self.model.name)}(models.Model):\r    "
        field: Field
        for field in self.model.fields.all():
            if field.exclude:
                continue
            s += FieldTransform(field).to_model_dot_py()

        s += "\r\r    "
        s += "__str__ = __repr__ = lambda self: f'{self.id}'"

        # s += f"\r\r    "
        # s += "def __str__(self):"
        # s += "\r        return f'{self.id}'"

        return s

    def to_admin_dot_py_class(self) -> str:
        fields = []
        search_fields = []
        list_display = []
        list_filter = []
        autocomplete_fields = []
        date_hierarchy = None
        field: Field
        for field in self.model.fields.all():
            if field.exclude:
                continue

            entry = FieldTransform(field).to_admin_dot_py_fields()
            if entry:
                fields.append(entry)

            entry = FieldTransform(field).to_admin_dot_py_search_fields()
            if entry:
                search_fields.append(entry)

            entry = FieldTransform(field).to_admin_dot_py_list_display()
            if entry:
                list_display.append(entry)

            entry = FieldTransform(field).to_admin_dot_py_list_filter()
            if entry:
                list_filter.append(entry)

            entry = FieldTransform(field).to_admin_dot_py_date_hierarchy()
            if not date_hierarchy and entry:
                date_hierarchy = entry

            entry = FieldTransform(field).to_admin_dot_py_autocomplete_fields()
            if entry:
                autocomplete_fields.append(entry)

        return (
            f"@admin.register({to_classname(self.model.name)})\r"
            f"class {to_classname(self.model.name)}Admin(admin.ModelAdmin):\r"
            f"    list_display=[{', '.join(list_display)}]\r"
            f"    list_filter=[{', '.join(list_filter)}]\r"
            f"    date_hierarchy={date_hierarchy}\r"
            f"    fields=[{', '.join(fields)}]\r"
            f"    search_fields=[{', '.join(search_fields)}]\r"
            f"    list_per_page=20\r"
            f"    \r"
        )

    # def to_admin_dot_py_register(self) -> str:
    #     model_class_name = to_classname(self.model.name)
    #     return f"admin.site.register({model_class_name}, {model_class_name}Admin)"


def format_file(file: Path) -> None:
    format_file_in_place(
        file,
        fast=False,
        write_back=WriteBack.YES,
        mode=Mode(
            target_versions={TargetVersion.PY311},
            line_length=80,
            experimental_string_processing=True,
        ),
    )


class ModelExporterDjango(ModelExporter):
    def __init__(self, cte: CookieCutterTemplateExpander):
        super().__init__(cte)
        self.app_dir = cte.config.config.get("custom_app_name")

    def export(self):
        app_dir: Path = self.create_app_dir()
        app_dir.mkdir(parents=True, exist_ok=True)

        model_py = self.create_model_py(app_dir)
        admin_py = self.create_admin_py(app_dir)
        self.create_views_py()
        self.patch_settings(app_dir)
        self.create_initial_data(app_dir)

        format_file(model_py)
        format_file(admin_py)

    def create_app_dir(self) -> Path:
        app_dir = Path(
            self.cookieCutterTemplateExpander.expand_parameter.output_dir,
            self.cookieCutterTemplateExpander.project_name_as_dirname(),
            self.app_dir,
        )
        app_dir.mkdir(exist_ok=True, parents=True)
        return app_dir

    def create_model_py(self, app_dir: Path) -> Path:

        models_py = app_dir.joinpath("models.py")

        output = f"# Created by Django LowCoder at {datetime.now()}\r\r"
        output += "from django.db import models\r"
        output += "from django.utils.translation import gettext_lazy as _\r"

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
        return models_py

    def reorder_data(self, model: Model, data):
        reordered_data = []
        for row in data:
            reordered_dict = {}
            for k, v in row.items():
                expanded_key = f"{self.app_dir}.{k}"
                reordered_dict[expanded_key] = v
            reordered_data.append(reordered_dict)
        return reordered_data

    def create_initial_data(self, app_dir: Path) -> None:

        initial_data_dir = app_dir.joinpath("initial_data")
        initial_data_dir.mkdir(parents=True, exist_ok=True)

        models: QuerySet[
            Model
        ] = self.cookieCutterTemplateExpander.project.transformationmapping.models
        model: Model
        for model in models.all():
            if model.exclude:
                continue
            data = model.transformation_headline.content
            data = self.reorder_data(model, data)
            if data:
                model_data_json = initial_data_dir.joinpath(
                    f"{to_varname(model.name)}.json"
                )
                model_data_json.write_text(json.dumps(data))

    def create_admin_py(self, app_dir) -> Path:

        admin_py = app_dir.joinpath("admin.py")

        models: QuerySet[
            Model
        ] = self.cookieCutterTemplateExpander.project.transformationmapping.models

        output = f"# Created by Django LowCoder at {datetime.now()}\r\r"
        output += "from django.contrib import admin\r"
        output += "from django.utils.translation import gettext_lazy as _\r"
        output += f"from {self.app_dir}.models import *\r\r"

        main_url = Path(
            "/admin/",
            self.app_dir,
            to_varname(models.filter(is_main_entity=True).first().name),
        )

        output += f"admin.site.site_header = '{self.cookieCutterTemplateExpander.project.name}'\r"
        output += f"admin.site.site_title = '{self.cookieCutterTemplateExpander.project.name}'\r"
        output += f"admin.site.site_url = '{main_url}'\r"

        # noinspection PyUnresolvedReferences
        model: Model
        for model in models.all():
            if model.exclude:
                continue
            output += "\r" + ModelTransform(model).to_admin_dot_py_class()

        admin_py.write_text(output)
        return admin_py

    def create_views_py(self):
        ...
        # create standard some standard list & crud views via generic views
        # mix special of cookiecutter template (... -> core) + programmatic code

    def patch_settings(self, app_dir: Path):
        # add app to INSTALLED_APPS or for cookiecutter-django LOCAL_APPS
        # output = f"INSTALLED_APPS += ['{self.cookieCutterTemplateExpander.project_name_as_dirname()}']"

        # base_py = app_dir.parent.joinpath("config", "settings", "base.py")
        # open and find LOCAL_APPS and replace '# Your stuff: custom apps go here'

        # solved via pathed cookiecutter template
        ...

    def patch_urls_and_menu(self):
        ...

    def start_local(self):
        """
        # add sqlite database entry to settings file, delete migration file with sequence
        python3.11 -m venv venv
        source venv/bin/activate
        pip3.11 install -r requirements/local.txt
        # pip3.11 install --upgrade pip
        python3.11 manage.py makemigrations --settings config.settings.local
        python3.11 manage.py migrate --settings config.settings.local
        python3.11 manage.py createsuperuser --settings config.settings.local
        python3.11 manage.py runserver --settings config.settings.local
        """
