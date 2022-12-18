from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as AuthLoginView
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic import FormView

from project.forms import RegisterForm, LoginForm, ProjectSettingsForm
from project.models import Project


class RegisterView(generic.CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'


class LoginView(AuthLoginView):
    form_class = LoginForm
    success_url = reverse_lazy('index')
    template_name = 'registration/login.html'


@method_decorator(login_required, name='dispatch')
class IndexView(generic.ListView):
    model = Project
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return Project.objects.filter(user=user)
        else:
            return QuerySet()


@method_decorator(login_required, name='dispatch')
class ProjectDetailView(generic.DetailView):
    model = Project


@method_decorator(login_required, name='dispatch')
class ProjectSettingsView(FormView):
    form_class = ProjectSettingsForm
    template_name = 'project/project_settings_detail.html'
