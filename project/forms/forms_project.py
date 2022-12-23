from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML
from django.forms import ModelForm, TypedChoiceField, RadioSelect, Form
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from project.models import Project


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
        fields = []


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
