from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False,
                                 help_text='Optional', label=_('Vorname'))
    last_name = forms.CharField(max_length=30, required=False,
                                help_text='Optional', label=_('Nachname'))
    email = forms.EmailField(max_length=254, help_text=_('Gib bitte eine '
                                                       'gültige '
                                                       'E-Mail-Adresse '
                                                       'an.'), label=_(
        'E-Mail-Adresse')),

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