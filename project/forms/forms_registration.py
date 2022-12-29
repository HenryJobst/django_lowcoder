from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML
from crispy_bootstrap5.bootstrap5 import FloatingField

from project.views.views_project import NEXT_URL_PARAM


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_action = "login"
        self.helper.form_class = "form-register"
        self.helper.layout = Layout(
            Fieldset(
                _("Nutzerdaten"),
                FloatingField("username"),
                FloatingField("first_name"),
                FloatingField("last_name"),
                FloatingField("email"),
                FloatingField("password1"),
                FloatingField("password2"),
            ),
            Submit("submit", _("Registrieren")),
        )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        """
        The __init__ function is called when an instance of the class is created.
        It initializes all the variables and sets up a layout for our form.
        The helper object allows us to set up how our form will be rendered,
        and what functionality to include.

        :param self: Reference the current instance of the class
        :param *args: Pass a non-keyworded, variable-length argument list
        :param **kwargs: Pass any additional keyword arguments that are passed to the constructor of the parent class
        :return: The layout of the form
        :doc-author: Trelent
        """
        """
        The __init__ function is called when an instance of the class is created.
        It initializes all the variables and sets up a layout for our form.
        The helper object allows us to set up how our form will be rendered,
        and what functionality to include.

        :param self: Reference the current instance of the class
        :param *args: Pass a non-keyworded, variable-length argument list
        :param **kwargs: Pass any additional keyword arguments that are passed to the constructor of the parent class
        :return: The layout of the form
        :doc-author: Trelent
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_action = reverse("login") + (
            "?" + NEXT_URL_PARAM + "=" + self.initial[NEXT_URL_PARAM]
            if NEXT_URL_PARAM in self.initial
            else ""
        )
        self.helper.form_class = "form-signin w-100 m-auto text-center"
        self.helper.layout = Layout(
            HTML(
                """<i class="feather-48 mb-4"
            data-feather="log-in"></i>"""
            ),
            Fieldset(
                _("Anmelden"),
                FloatingField("username"),
                FloatingField("password"),
            ),
            Submit("submit", _("Anmelden")),
            HTML(
                """
            <div class="mt-3">
            <a href="{% url 'password_reset' %}">
            {{_('Passwort vergessen?')}}</a>
            </div>
            <div class="mt-1">
            <a href="{% url 'register' %}">
            {{_('Registrieren')}}</a>
            </div>
            """
            ),
        )

    class Meta:
        fields = [
            "username",
            "password",
        ]
