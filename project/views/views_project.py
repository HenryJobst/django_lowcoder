from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from project.forms.forms_project import ProjectEditForm, ProjectDeleteForm
from project.models import Project


@method_decorator(login_required, name='dispatch')
class ProjectDetailView(DetailView):
    model = Project


@method_decorator(login_required, name='dispatch')
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectEditForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectEditForm


@method_decorator(login_required, name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    form_class = ProjectDeleteForm
    success_url = reverse_lazy('index')
