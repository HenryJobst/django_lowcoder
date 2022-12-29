from typing import List

from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Field, Row, Column, Div
from django.forms import (
    ModelForm,
    TypedChoiceField,
    RadioSelect,
    Form,
    FileField,
    ClearableFileInput,
    IntegerField,
    CharField,
)
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from pandas import DataFrame

from project.models import (
    Project,
    ProjectSettings,
    Model,
    Field as ModelField,
    TransformationFile,
    VALID_MIMETYPES,
)
from project.services.importer import Importer


class ProjectEditForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "m-auto"
        self.helper.layout = Layout(
            Fieldset(
                _("Projekteinstellungen"),
                FloatingField("name"),
                FloatingField("description"),
            ),
            HTML(
                "{% if project %}"
                + '<a class="btn btn-primary mb-3" href="{% url \'project_create_file\' project.id %}?next={{'
                'next_url}}">' + _("Datei importieren") + "</a>" + "{% endif %}"
            ),
            Fieldset(
                "",
                Submit("submit", _("Speichern")),
                HTML(
                    '<a class="btn btn-secondary ms-1" href="{% url \'index\' %}">'
                    + _("Abbrechen")
                    + "</a>"
                ),
            ),
        )

    class Meta:
        model = Project
        fields = ["name", "description"]


class ProjectDeleteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "w-100 m-auto text-center"
        self.helper.layout = Layout(
            HTML(
                """<p>Wollen Sie das Projekt <b>{{ object.name }}</b> wirklich
            löschen?</p>"""
            ),
            Submit("submit", _("Bestätigen")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'index\' %}">'
                + _("Abbrechen")
                + "</a>"
            ),
        )

    class Meta:
        model = Project
        fields: List = []


class ProjectDeployForm(Form):

    type = TypedChoiceField(
        label=_("Starte Anwendung "),
        choices=((0, "lokal"), (1, "via Docker")),
        coerce=lambda x: bool(int(x)),
        widget=RadioSelect,
        initial="0",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "w-100 m-auto"
        self.helper.layout = Layout(
            Fieldset(_("Projekt generieren"), "type"),
            Submit("submit", _("Start")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'index\' %}">'
                + _("Abbrechen")
                + "</a>"
            ),
        )

    class Meta:
        fields = ["type"]


class ProjectEditSettingsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "m-auto"
        self.helper.layout = Layout(
            Fieldset(
                _("weitere Projekteinstellungen"),
                FloatingField("admin_name"),
                FloatingField("admin_password"),
                FloatingField("demo_user_name"),
                FloatingField("demo_user_password"),
                FloatingField("domain_name"),
            ),
            Submit("submit", _("Speichern")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'project_detail\' object.project.id %}">'
                + _("Abbrechen")
                + "</a>"
            ),
        )

    class Meta:
        model = ProjectSettings
        fields = [
            "admin_name",
            "admin_password",
            "demo_user_name",
            "demo_user_password",
            "domain_name",
        ]


class ProjectEditModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "m-auto"
        self.helper.layout = Layout(
            Fieldset(
                _("Tabelle"),
                FloatingField("name"),
                Field("is_main_entity", label=_("Haupt-Tabelle")),
            ),
            Submit("submit", _("Speichern")),
            HTML(
                "{% if object.id %}"
                + '<a class="btn btn-secondary" href="{% url \'project_detail_model\' object.id %}">'
                + _("Abbrechen")
                + "</a>"
                + "{% elif project %}"
                + '<a class="btn btn-secondary" href="{% url \'project_list_models\' project.id %}">'
                + _("Abbrechen")
                + "</a>"
                + "{% endif %}"
            ),
        )

    class Meta:
        model = Model
        fields = ["name", "is_main_entity"]


class ProjectDeleteModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "w-100 m-auto text-center"
        self.helper.layout = Layout(
            HTML(
                """<p>Wollen Sie die Tabelle <b>{{ object.name }}</b>
                wirklich löschen?</p>"""
            ),
            Submit("submit", _("Bestätigen")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'project_list_models\' '
                "object.transformation_mapping.project.id "
                '%}">' + _("Abbrechen") + "</a>"
            ),
        )

    class Meta:
        model = Model
        fields: List = []


class ProjectEditFieldForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "m-auto"
        self.helper.layout = Layout(
            Fieldset(
                _("Spalte"),
                FloatingField("name"),
                FloatingField("datatype"),
                FloatingField("datatype_length"),
                FloatingField("default_value"),
                FloatingField("foreign_key_entity"),
                Field("is_unique"),
                Field("use_index"),
                Field("show_in_list"),
            ),
            Submit("submit", _("Speichern")),
            HTML(
                "{% if object.id %}"
                + '<a class="btn btn-secondary" href="{% url \'project_detail_field\' object.id %}">'
                + _("Abbrechen")
                + "</a>"
                + "{% elif model %}"
                + '<a class="btn btn-secondary" href="{% url \'project_list_fields\' model.id %}">'
                + _("Abbrechen")
                + "</a>"
                + "{% endif %}"
            ),
        )

    class Meta:
        model = ModelField
        fields = [
            "name",
            "datatype",
            "datatype_length",
            "default_value",
            "foreign_key_entity",
            "is_unique",
            "use_index",
            "show_in_list",
        ]


class ProjectDeleteFieldForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "w-100 m-auto text-center"
        self.helper.layout = Layout(
            HTML(
                """<p>Wollen Sie die Spalte <b>{{ object.name }}</b>
                wirklich
            löschen?</p>"""
            ),
            Submit("submit", _("Bestätigen")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'project_list_models\' '
                'model.transformation_mapping.project.id %}">' + _("Abbrechen") + "</a>"
            ),
        )

    class Meta:
        model = ModelField
        fields: List = []


class ProjectEditFileForm(ModelForm):
    file = FileField(
        label=_("Datei"),
        localize=True,
        help_text=_("Wählen sie eine Datei zum Import."),
        widget=ClearableFileInput(attrs={"accept": ",".join(VALID_MIMETYPES)}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "m-auto"
        self.helper.layout = Layout(
            Field("file"),
            Submit("submit", _("Speichern")),
            HTML(
                "{% if object.id %}"
                + '<a class="btn btn-secondary" href="{% url \'project_list_files\' '
                'object.transformation_mapping.project.id %}">'
                + _("Abbrechen")
                + "</a>"
                + "{% elif project %}"
                + '<a class="btn btn-secondary" href="{% url \'project_list_files\' project.id %}">'
                + _("Abbrechen")
                + "</a>"
                + "{% endif %}"
            ),
        )

    class Meta:
        model = TransformationFile
        fields = ["file"]


class ProjectDeleteFileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "w-100 m-auto text-center"
        self.helper.layout = Layout(
            HTML(
                """<p>Wollen Sie die Datei <b>{{ object.file }}</b>
                wirklich löschen?</p>"""
            ),
            Submit("submit", _("Bestätigen")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'project_list_files\' '
                "object.transformation_mapping.project.id "
                '%}">' + _("Abbrechen") + "</a>"
            ),
        )

    class Meta:
        model = TransformationFile
        fields: List = []


def var_name(sheet_name: str, v_name: str) -> str:
    return slugify(sheet_name.lower() + "_" + v_name)


class ProjectImportFileForm(Form):

    # noinspection PyUnusedLocal
    def __init__(self, **kwargs):
        super().__init__()
        self.helper = FormHelper()
        self.helper.layout = Layout()

    def register_field(self, field_name, field):
        setattr(
            ProjectImportFileForm,
            field_name,
            field,
        )
        self.fields[field_name] = self.__getattribute__(field_name)
        self.declared_fields[field_name] = self.__getattribute__(field_name)
        self.base_fields[field_name] = self.__getattribute__(field_name)

    def init_helper(self, df_by_sheet, file_pk: int):
        tab_holder: TabHolder = TabHolder()
        sheet: str
        df_settings: tuple[DataFrame, Importer.SheetReaderParams]
        for sheet, df_settings in df_by_sheet.items():
            df: DataFrame = df_settings[0]
            settings: Importer.SheetReaderParams = df_settings[1]
            self.register_fields(sheet, settings)
            tab_holder.fields.append(
                Tab(
                    f"{_('Tabelle:')} {sheet}",
                    Div(
                        HTML("<h5>" + _("Importeinstellungen") + "</h5>"),
                        css_class="mt-2",
                    ),
                    Div(
                        Row(
                            Column(
                                FloatingField(
                                    Field(
                                        var_name(sheet, "header"),
                                        hx_get=reverse_lazy(
                                            "project_import_file",
                                            kwargs={"pk": file_pk},
                                        ),
                                        hx_include=("#" + var_name(sheet, "settings")),
                                        hx_target=("#" + var_name(sheet, "table-head")),
                                        hx_select=("#" + var_name(sheet, "table-head")),
                                    )
                                ),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            Column(
                                FloatingField(var_name(sheet, "usecols")),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            Column(
                                FloatingField(var_name(sheet, "nrows")),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            css_class="form-row",
                        ),
                        Row(
                            Column(
                                FloatingField(var_name(sheet, "skiprows")),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            Column(
                                FloatingField(var_name(sheet, "skipfooter")),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            css_class="form-row",
                        ),
                        css_id=var_name(sheet, "settings"),
                    ),
                    HTML("<hr>"),
                    HTML("<h5>" + _("Tabellenausschnitt") + "</h5>"),
                    Div(
                        HTML("<h6>" + _("Kopfteil") + "</h6>"),
                        Div(
                            HTML(
                                df.head().to_html(
                                    table_id=var_name(sheet, "table-head"),
                                    classes="table table-striped table-bordered table-sm ",
                                )
                            ),
                            css_class="table-responsive",
                        ),
                        css_class="form-row",
                    ),
                    Div(
                        HTML("<h6>" + _("Fußteil") + "</h6>"),
                        Div(
                            HTML(
                                df.tail().to_html(
                                    table_id=var_name(sheet, "table-tail"),
                                    classes="table table-striped table-bordered table-sm ",
                                )
                            ),
                            css_class="table-responsive",
                        ),
                        css_class="form-row",
                    ),
                )
            )

        self.helper.layout.fields.append(tab_holder)
        self.helper.layout.fields.append(Submit("submit", _("Import")))

    def register_fields(self, sheet, settings):
        self.register_field(
            var_name(sheet, "header"),
            IntegerField(
                label=_("Tabellenkopf"),
                help_text=_("Zeile für den Tabellenkopf (0-basiert)"),
                required=True,
                initial=settings.header,
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, "usecols"),
            CharField(
                label=_("Tabellenbereich"),
                help_text=_(
                    "Ausschnitt der Tabelle (Form: 'A:E' or 'A,C,E:F' - leer: alle Spalten)"
                ),
                required=False,
                initial=settings.usecols,
            ),
        )
        self.register_field(
            var_name(sheet, "nrows"),
            IntegerField(
                label=_("Zeilenanzahl"),
                help_text=_("Anzahl der Zeilen (leer: alle Zeilen)"),
                required=False,
                initial=settings.nrows,
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, "skiprows"),
            IntegerField(
                label=_("Übersprungene Zeilen am Anfang"),
                help_text=_(
                    "Anzahl der zu überspringenden Zeilen am Anfang (leer: keine Zeilen)"
                ),
                required=False,
                initial=settings.skiprows,
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, "skipfooter"),
            IntegerField(
                label=_("Ausgelassene Zeilen am Ende"),
                help_text=_(
                    "Anzahl der ausgelassenen Zeilen am Ende (0: keine Zeilen)"
                ),
                required=True,
                initial=settings.skipfooter,
                min_value=0,
            ),
        )
