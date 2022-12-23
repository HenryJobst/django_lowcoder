from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView

from project.forms.forms_project import (
    ProjectEditForm,
    ProjectDeleteForm,
    ProjectDeployForm,
)
from project.services.cookiecutter_templete_expander import CookieCutterTemplateExpander
from project.views.mixins import ModelUserFieldPermissionMixin
from project.services.session import *


class ProjectDetailView(LoginRequiredMixin, ModelUserFieldPermissionMixin, DetailView):
    model = Project


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectEditForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        set_selection(self.request, self.object.id)
        return super().get_success_url()


class ProjectUpdateView(LoginRequiredMixin, ModelUserFieldPermissionMixin, UpdateView):
    model = Project
    form_class = ProjectEditForm

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next")  # pass `next`
        # parameter received from previous page to the context
        return context

    def get_success_url(self):
        set_selection(self.request, self.kwargs["pk"])
        next_url = self.request.GET.get("next")
        return next_url if next_url else reverse_lazy("index")

    def get(self, request, *args, **kwargs):
        set_selection(self.request, self.kwargs["pk"])
        return super().get(request, *args, **kwargs)


class ProjectDeleteView(LoginRequiredMixin, ModelUserFieldPermissionMixin, DeleteView):
    model = Project
    form_class = ProjectDeleteForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        reset_selection(request=self.request, pk=(self.kwargs["pk"]))
        return super().form_valid(form)


class ProjectDeployView(LoginRequiredMixin, ModelUserFieldPermissionMixin, FormView):
    template_name = "project/project_deploy.html"
    form_class = ProjectDeployForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        pk = self.kwargs["pk"]
        project: Project = get_object_or_404(Project, pk=pk)

        self.deploy_project(self.request.user, project, self.request.POST)
        return super().form_valid(form)

    @staticmethod
    def deploy_project(user: User, project: Project, post_dict: QueryDict) -> None:
        expander = CookieCutterTemplateExpander(user, project, post_dict)
        expander.expand()


class ProjectSelectView(
    LoginRequiredMixin, ModelUserFieldPermissionMixin, BaseDetailView
):
    model = Project

    def get(self, request, *args, **kwargs):
        pk: int = self.kwargs["pk"]
        toggle_selection(request, pk)
        return redirect(reverse_lazy("index"))
