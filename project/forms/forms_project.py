from typing import List

from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Field
from django.forms import (
    ModelForm,
    TypedChoiceField,
    RadioSelect,
    Form,
    FileField,
    ClearableFileInput,
)
from django.utils.translation import gettext_lazy as _

from project.models import (
    Project,
    ProjectSettings,
    Model,
    Field as ModelField,
    TransformationFile,
    VALID_MIMETYPES,
)


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
