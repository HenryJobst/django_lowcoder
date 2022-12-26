from typing import List

from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Field
from django.forms import ModelForm, TypedChoiceField, RadioSelect, Form
from django.utils.translation import gettext_lazy as _

import project.models
from project.models import Project, ProjectSettings, Model


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
            Submit("submit", _("Speichern")),
            HTML(
                '<a class="btn btn-secondary" href="{% url \'index\' %}">'
                + _("Abbrechen")
                + "</a>"
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
                '<a class="btn btn-secondary" href="{% url \'index\' %}">'
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
                '<a class="btn btn-secondary" href="{% url \'index\' %}">'
                + _("Abbrechen")
                + "</a>"
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
                '<a class="btn btn-secondary" href="{% url \'project_detail\' object.id '
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
                '<a class="btn btn-secondary" href="{% url \'index\' %}">'
                + _("Abbrechen")
                + "</a>"
            ),
        )

    class Meta:
        model = project.models.Field
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
                '<a class="btn btn-secondary" href="{% url \'project_detail\' object.id '
                '%}">' + _("Abbrechen") + "</a>"
            ),
        )

    class Meta:
        model = Model
        fields: List = []
