from crispy_bootstrap5.bootstrap5 import FloatingField  # type: ignore
from crispy_forms.bootstrap import TabHolder, Tab  # type: ignore
from crispy_forms.helper import FormHelper  # type: ignore
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Field as LayoutField, Row, Column, Div  # type: ignore
from django.forms import (
    ModelForm,
    TypedChoiceField,
    RadioSelect,
    Form,
    FileField,
    ClearableFileInput,
    IntegerField,
    CharField,
    Textarea,
    ModelChoiceField,
)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from project.models import (
    Project,
    ProjectSettings,
    Field as ModelField,
    VALID_MIMETYPES,
    CodeTemplate,
)
from project.services.deploytype import Deploytype
from project.services.importer import *

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
                _("Project Settings"),
                FloatingField("name"),
                FloatingField("description"),
            ),
            HTML(
                "{% if project %}"
                '<a class="btn btn-primary mb-3" href="'
                "{% url 'project_create_file' project.id %}?next={{next_url}}\">"
                + _("Import File")
                + "</a>{% endif %}"
            ),
            Fieldset(
                "",
                Submit("submit", _("Save")),
                HTML(
                    '<a class="btn btn-secondary ms-1" href="{% url \'index\' %}">'
                    + _("Cancel")
                    + "</a>"
                ),
            ),
        )

    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {
            "description": Textarea(attrs={"style": "height: 8rem"}),
        }


class ProjectDeleteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "w-100 m-auto text-center"
        self.helper.layout = Layout(
            HTML(
                "{% load i18n %}"
                + "<p>"
                + _("Are you really shure to delete the project <b>%(name)s</b>?")
                % {"name": self.instance.name}
                + "</p>"
            ),
            Submit("submit", _("Confirm")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'index\' %}">'
                + _("Cancel")
                + "</a>"
            ),
        )

    class Meta:
        model = Project
        fields: List = []


class ProjectDeployForm(Form):

    app_type = ModelChoiceField(
        label=_("Code Template"),
        queryset=CodeTemplate.objects.all(),
        empty_label=_(
            "Contact a administrator to register at least one cookiecutter code template."
        ),
        initial="0",
        required=True,
        blank=False,
        help_text=_("URI or Path to an existing cookiecutter code template."),
    )

    deploy_type = TypedChoiceField(
        label=_("Deployment Type"),
        choices=Deploytype.choices,
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
            Fieldset(
                _("Generate Project"),
                LayoutField("app_type"),
                LayoutField("deploy_type"),
            ),
            Submit("submit", _("Start")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'index\' %}">'
                + _("Cancel")
                + "</a>"
            ),
        )

    class Meta:
        fields = ["app_type", "deploy_type"]


class ProjectDeploySummaryForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "w-100 m-auto"
        self.helper.layout = Layout(
            Fieldset(
                _("Generate Project"),
                HTML(_("Summary")),
                HTML(""" ... """),
            ),
            Submit("submit", _("Start")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'index\' %}">'
                + _("Cancel")
                + "</a>"
            ),
        )

    class Meta:
        fields = []


class ProjectEditSettingsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "m-auto"
        self.helper.layout = Layout(
            Fieldset(
                _("Project settings"),
                FloatingField("admin_name"),
                FloatingField("admin_password"),
                FloatingField("demo_user_name"),
                FloatingField("demo_user_password"),
                FloatingField("domain_name"),
                FloatingField("code_template"),
            ),
            Submit("submit", _("Save")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'project_detail\' object.project.id %}">'
                + _("Cancel")
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
            "code_template",
        ]


class ProjectEditModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "m-auto"
        self.helper.layout = Layout(
            Fieldset(
                _("Table"),
                LayoutField("exclude"),
                FloatingField("name"),
                FloatingField("description"),
                LayoutField("is_main_entity", label=_("Main Table")),
            ),
            Submit("submit", _("Save")),
            HTML(
                "{% if object.id %}"
                + '<a class="btn btn-secondary" href="{% url \'project_detail_model\' object.id %}">'
                + _("Cancel")
                + "</a>"
                + "{% elif project %}"
                + '<a class="btn btn-secondary" href="{% url \'project_list_models\' project.id %}">'
                + _("Cancel")
                + "</a>"
                + "{% endif %}"
            ),
        )

    class Meta:
        model = Model
        fields = ["name", "description", "is_main_entity", "exclude"]
        widgets = {
            "description": Textarea(attrs={"style": "height: 8rem"}),
        }


class ProjectDeleteModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "w-100 m-auto text-center"
        self.helper.layout = Layout(
            HTML(
                "<p>"
                + _("Are you really shure to delete the table <b>%(name)s</b>?")
                % {"name": self.instance.name}
                + "</p>"
            ),
            Submit("submit", _("Confirm")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'project_list_models\' '
                "object.transformation_mapping.project.id "
                '%}">' + _("Cancel") + "</a>"
            ),
        )

    class Meta:
        model = Model
        fields: List = []


class ProjectEditFieldForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            # noinspection PyUnresolvedReferences
            self.fields["foreign_key_entity"].queryset = Model.objects.filter(
                transformation_mapping=self.instance.model.transformation_mapping
            )
        else:
            # noinspection PyUnresolvedReferences
            self.fields["foreign_key_entity"].queryset = Model.objects.none()

        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "m-auto"
        self.helper.layout = Layout(
            Fieldset(
                _("Column"),
                LayoutField("exclude"),
                FloatingField("name"),
                FloatingField("description"),
                Row(
                    Column(
                        FloatingField("datatype"),
                    ),
                    Column(
                        FloatingField("max_length"),
                    ),
                    Column(
                        FloatingField("default_value"),
                    ),
                ),
                Row(
                    Column(
                        FloatingField("max_digits"),
                    ),
                    Column(
                        FloatingField("decimal_places"),
                    ),
                ),
                FloatingField("choices"),
                FloatingField("foreign_key_entity"),
                Row(
                    Column(
                        LayoutField("blank"),
                    ),
                    Column(LayoutField("null")),
                ),
                Row(
                    Column(
                        LayoutField("is_unique"),
                    ),
                    Column(
                        LayoutField("use_index"),
                    ),
                ),
                Row(
                    Column(
                        LayoutField("show_in_list"),
                    ),
                    Column(
                        LayoutField("show_in_detail"),
                    ),
                ),
            ),
            Submit("submit", _("Save")),
            HTML(
                "{% if model %}"
                + '<a class="btn btn-secondary" href="{% url \'project_list_fields\' model.id %}">'
                + _("Cancel")
                + "</a>"
                + "{% endif %}"
            ),
        )

    class Meta:
        model = ModelField
        fields = [
            "name",
            "description",
            "datatype",
            "max_length",
            "max_digits",
            "decimal_places",
            "default_value",
            "choices",
            "foreign_key_entity",
            "blank",
            "null",
            "is_unique",
            "use_index",
            "show_in_list",
            "show_in_detail",
            "exclude",
        ]
        widgets = {
            "description": Textarea(attrs={"style": "height: 8rem"}),
            "choices": Textarea(attrs={"style": "height: 8rem"}),
        }


class ProjectDeleteFieldForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "w-100 m-auto text-center"
        self.helper.layouet = Layout(
            HTML(
                "<p>"
                + _("Are you really shure to delete the column <b>%(name)s</b>?")
                % {"name": self.instance.name}
                + "</p>"
            ),
            Submit("submit", _("Confirm")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'project_list_models\' '
                'model.transformation_mapping.project.id %}">' + _("Cancel") + "</a>"
            ),
        )

    class Meta:
        model = ModelField
        fields: List = []


class ProjectEditFileForm(ModelForm):
    file = FileField(
        label=_("File"),
        localize=True,
        help_text=_("Select a file for import."),
        widget=ClearableFileInput(attrs={"accept": ",".join(VALID_MIMETYPES)}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_class = "m-auto"
        self.helper.layout = Layout(
            LayoutField("file"),
            Submit("submit", _("Save")),
            HTML(
                "{% if object.id %}"
                + '<a class="btn btn-secondary" href="{% url \'project_list_files\' '
                'object.transformation_mapping.project.id %}">'
                + _("Cancel")
                + "</a>"
                + "{% elif project %}"
                + '<a class="btn btn-secondary" href="{% url \'project_list_files\' project.id %}">'
                + _("Cancel")
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
                "<p>"
                + _("Are you really shure to delete the file <b>%(name)s</b>?")
                % {"name": self.instance.file.name}
                + "</p>"
            ),
            Submit("submit", _("Confirm")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'project_list_files\' '
                "object.transformation_mapping.project.id "
                '%}">' + _("Cancel") + "</a>"
            ),
        )

    class Meta:
        model = TransformationFile
        fields: List = []


def var_name(sheet_name: str, v_name: str) -> str:
    return slugify(sheet_name.lower() + "_" + v_name).replace("-", "_")


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
                    f"{_('Table:')} {sheet}",
                    Div(
                        HTML("<h5>" + _("Import Settings") + "</h5>"),
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
                    HTML("<h5>" + _("Table Section") + "</h5>"),
                    Div(
                        Div(
                            Row(
                                Column(
                                    HTML("<h6>" + _("Head") + "</h6>"),
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
                                        n=settings.get(
                                            TABLE_PARAM_HEAD_ROWS,
                                            DEFAULT_HEAD_TAIL_ROWS,
                                        )
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
                                    HTML("<h6>" + _("Tail") + "</h6>"),
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
                                        n=settings.get(
                                            TABLE_PARAM_TAIL_ROWS,
                                            DEFAULT_HEAD_TAIL_ROWS,
                                        )
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
                label=_("Table Head"),
                help_text=_("Row for the table header (0-based)"),
                required=True,
                initial=settings.get(READ_PARAM_HEADER),
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, READ_PARAM_USECOLS),
            CharField(
                label=_("Table Section"),
                help_text=_(
                    "Table section (form: 'A:E' or 'A,C,E:F' - empty: all columns)"
                ),
                required=False,
                initial=settings.get(READ_PARAM_USECOLS),
            ),
        )
        self.register_field(
            var_name(sheet, READ_PARAM_NROWS),
            IntegerField(
                label=_("Row Count"),
                help_text=_("Count of rows (empty: all rows until table end)"),
                required=False,
                initial=settings.get(READ_PARAM_NROWS),
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, READ_PARAM_SKIPROWS),
            IntegerField(
                label=_("Skipped Rows at the Beginning"),
                help_text=_(
                    "Number of skipped rows at the beginning of the table (empty: skip no rows)"
                ),
                required=False,
                initial=settings.get(READ_PARAM_SKIPROWS),
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, READ_PARAM_SKIPFOOTER),
            IntegerField(
                label=_("Skipped Rows at the End"),
                help_text=_(
                    "Number of skipped rows an the end of the table (0: skip no rows)"
                ),
                required=True,
                initial=settings.get(READ_PARAM_SKIPFOOTER),
                min_value=0,
            ),
        )
        self.register_field(
            var_name(sheet, TABLE_PARAM_HEAD_ROWS),
            IntegerField(
                label=_("Count of Rows"),
                initial=settings.get(TABLE_PARAM_HEAD_ROWS, DEFAULT_HEAD_TAIL_ROWS),
                min_value=3,
                max_value=100,
                required=True,
            ),
        )
        self.register_field(
            var_name(sheet, TABLE_PARAM_TAIL_ROWS),
            IntegerField(
                label=_("Count of Rows"),
                initial=settings.get(TABLE_PARAM_TAIL_ROWS, DEFAULT_HEAD_TAIL_ROWS),
                min_value=3,
                max_value=100,
                required=True,
            ),
        )
