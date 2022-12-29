from typing import Any

from django.contrib.auth.views import LoginView as AuthLoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from project.forms.forms_registration import RegisterForm, LoginForm
from project.views.views_project import NEXT_URL_PARAM, NextMixin


class RegisterView(CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"


class LoginView(NextMixin, AuthLoginView):

    form_class = LoginForm
    template_name = "registration/login.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data[NEXT_URL_PARAM] = self.request.GET.get(NEXT_URL_PARAM)
        return data

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        if NEXT_URL_PARAM in self.request.GET:
            initial[NEXT_URL_PARAM] = self.request.GET.get(NEXT_URL_PARAM)
        return initial
