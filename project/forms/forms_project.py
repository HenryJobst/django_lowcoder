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
from project.services.importer import (
    SheetReaderParams,
    READ_PARAM_HEADER,
    READ_PARAM_USECOLS,
    READ_PARAM_NROWS,
    READ_PARAM_SKIPROWS,
    READ_PARAM_SKIPFOOTER,
    TABLE_PARAM_HEAD_ROWS,
    TABLE_PARAM_TAIL_ROWS,
    DEFAULT_HEAD_TAIL_ROWS,
)

TABLE_FULL = "table-full"
TABLE_HEAD = "table-head"
TABLE_TAIL = "table-tail"

SETTINGS = "settings"


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


def var_name_id(sheet_name: str, v_name: str) -> str:
    return "#" + var_name(sheet_name, v_name)


class FloatingFieldWithHtmx(FloatingField):
    def __init__(self, file_pk, sheet, *args, **kwargs):
        self.add_to_kwargs("hx_get", get_success_url(file_pk), kwargs)
        self.add_to_kwargs("hx_include", var_name_id(sheet, SETTINGS), kwargs)
        self.add_to_kwargs("hx_target", var_name_id(sheet, TABLE_FULL), kwargs)
        self.add_to_kwargs("hx_select", var_name_id(sheet, TABLE_FULL), kwargs)
        super().__init__(*args, **kwargs)

    @staticmethod
    def add_to_kwargs(key, value, kwargs):
        kwargs[key] = value


def get_success_url(file_pk):
    return reverse_lazy("project_import_file", kwargs={"pk": file_pk})


class ProjectImportFileForm(Form):

    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
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
        df_settings: tuple[DataFrame, SheetReaderParams]
        for sheet, df_settings in df_by_sheet.items():
            df: DataFrame = df_settings[0]
            settings: SheetReaderParams = df_settings[1]
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
                                FloatingFieldWithHtmx(
                                    file_pk,
                                    sheet,
                                    var_name(sheet, READ_PARAM_HEADER),
                                ),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            Column(
                                FloatingFieldWithHtmx(
                                    file_pk,
                                    sheet,
                                    var_name(sheet, READ_PARAM_USECOLS),
                                ),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            Column(
                                FloatingFieldWithHtmx(
                                    file_pk,
                                    sheet,
                                    var_name(sheet, READ_PARAM_NROWS),
                                ),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            css_class="form-row",
                        ),
                        Row(
                            Column(
                                FloatingFieldWithHtmx(
                                    file_pk,
                                    sheet,
                                    var_name(sheet, READ_PARAM_SKIPROWS),
                                ),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            Column(
                                FloatingFieldWithHtmx(
                                    file_pk,
                                    sheet,
                                    var_name(sheet, READ_PARAM_SKIPFOOTER),
                                ),
                                css_class="form-group col-md-4 mb-0",
                            ),
                            css_class="form-row",
                        ),
                        css_id=var_name(sheet, SETTINGS),
                    ),
                    HTML("<hr>"),
                    HTML("<h5>" + _("Tabellenausschnitt") + "</h5>"),
                    Div(
                        Div(
                            Row(
                                Column(
                                    HTML("<h6>" + _("Kopfteil") + "</h6>"),
                                    css_class="form-group col-md-10 mb-0",
                                ),
                                Column(
                                    FloatingFieldWithHtmx(
                                        file_pk,
                                        sheet,
                                        var_name(sheet, TABLE_PARAM_HEAD_ROWS),
                                    ),
                                    css_class="form-group col-md-2 mb-0",
                                ),
                                css_class="form-row",
                            ),
                            Div(
                                HTML(
                                    df.head(
                                        n=settings.get(TABLE_PARAM_HEAD_ROWS)
                                    ).to_html(
                                        table_id=var_name(sheet, TABLE_HEAD),
                                        classes="table table-striped table-bordered table-sm",
                                        justify="left",
                                    )
                                ),
                                css_class="table-responsive",
                            ),
                            css_class="form-row mt-3",
                        ),
                        Div(
                            Row(
                                Column(
                                    HTML("<h6>" + _("Fußteil") + "</h6>"),
                                    css_class="form-group col-md-10 mb-0",
                                ),
                                Column(
                                    FloatingFieldWithHtmx(
                                        file_pk,
                                        sheet,
                                        var_name(sheet, TABLE_PARAM_TAIL_ROWS),
                                    ),
                                    css_class="form-group col-md-2 mb-0",
                                ),
                                css_class="form-row",
                            ),
                            Div(
                                HTML(
                                    df.tail(
                                        n=settings.get(TABLE_PARAM_TAIL_ROWS)
                                    ).to_html(
                                        table_id=var_name(sheet, TABLE_TAIL),
                                        classes="table table-striped table-bordered table-sm",
                                        justify="left",
                                    )
                                ),
                                css_class="table-responsive",
                            ),
                            css_class="form-row mt-3",
                        ),
                        css_id=var_name(sheet, TABLE_FULL),
                    ),
                )
            )

        self.helper.layout.fields.append(tab_holder)
        self.helper.layout.fields.append(Submit("submit", _("Import")))

    def register_fields(self, sheet: str, settings: SheetReaderParams):
        self.register_field(
            var_name(sheet, READ_PARAM_HEADER),
            IntegerField(
                label=_("Tabellenkopf"),
                help_text=_("Zeile für den Tabellenkopf (0-basiert)"),
                required=True,
                initial=settings.get(READ_PARAM_HEADER),
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, READ_PARAM_USECOLS),
            CharField(
                label=_("Tabellenbereich"),
                help_text=_(
                    "Ausschnitt der Tabelle (Form: 'A:E' or 'A,C,E:F' - leer: alle Spalten)"
                ),
                required=False,
                initial=settings.get(READ_PARAM_USECOLS),
            ),
        )
        self.register_field(
            var_name(sheet, READ_PARAM_NROWS),
            IntegerField(
                label=_("Zeilenanzahl"),
                help_text=_("Anzahl der Zeilen (leer: alle Zeilen)"),
                required=False,
                initial=settings.get(READ_PARAM_NROWS),
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, READ_PARAM_SKIPROWS),
            IntegerField(
                label=_("Übersprungene Zeilen am Anfang"),
                help_text=_(
                    "Anzahl der zu überspringenden Zeilen am Anfang (leer: keine Zeilen)"
                ),
                required=False,
                initial=settings.get(READ_PARAM_SKIPROWS),
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, READ_PARAM_SKIPFOOTER),
            IntegerField(
                label=_("Ausgelassene Zeilen am Ende"),
                help_text=_(
                    "Anzahl der ausgelassenen Zeilen am Ende (0: keine Zeilen)"
                ),
                required=True,
                initial=settings.get(READ_PARAM_SKIPFOOTER),
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, TABLE_PARAM_HEAD_ROWS),
            IntegerField(
                label=_("Zeilenanzahl"),
                initial=settings.get(TABLE_PARAM_HEAD_ROWS, DEFAULT_HEAD_TAIL_ROWS),
                min_value=3,
                max_value=100,
                required=True,
            ),
        )
        self.register_field(
            var_name(sheet, TABLE_PARAM_TAIL_ROWS),
            IntegerField(
                label=_("Zeilenanzahl"),
                initial=settings.get(TABLE_PARAM_TAIL_ROWS, DEFAULT_HEAD_TAIL_ROWS),
                min_value=3,
                max_value=100,
                required=True,
            ),
        )
