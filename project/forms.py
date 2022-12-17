from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset
from crispy_bootstrap5.bootstrap5 import FloatingField


class RegisterForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'login'
        self.helper.form_class = 'form-register'
        self.helper.layout = Layout(
            Fieldset(
                _('Nutzerdaten'),
                FloatingField('username'),
                FloatingField('first_name'),
                FloatingField('last_name'),
                FloatingField('email'),
                FloatingField('password1'),
                FloatingField('password2')
                ),
            Submit('submit', _('Registrieren')),
            )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            ]


class LoginForm(AuthenticationForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper(self)
    #     self.helper.form_method = 'post'
    #     self.helper.form_action = 'login'
    #     self.helper.form_class = 'form-signin'
    #     self.helper.layout = Layout(
    #         Fieldset(
    #             _('Anmelden'),
    #             FloatingField('username'),
    #             FloatingField('password'),
    #             ),
    #         Submit('submit', _('Anmelden')),
    #         )

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            ]
