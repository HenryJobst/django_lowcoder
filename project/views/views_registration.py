from django.contrib.auth.views import LoginView as AuthLoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from project.forms.forms_registration import RegisterForm, LoginForm


class RegisterView(CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"


class LoginView(AuthLoginView):
    form_class = LoginForm
    success_url = reverse_lazy("index")
    template_name = "registration/login.html"
