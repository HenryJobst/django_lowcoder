from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet, Max
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import CreateView, \
    DeleteView, \
    UpdateView, \
    FormView

from project.forms.forms_project import (
    ProjectEditForm,
    ProjectDeleteForm,
    ProjectDeployForm,
    ProjectEditSettingsForm,
    ProjectEditModelForm,
    ProjectDeleteModelForm,
    )
from project.models import TransformationMapping, ProjectSettings, generate_random_admin_password
from project.services.cookiecutter_templete_expander import \
    CookieCutterTemplateExpander
from project.services.session import *
from project.views.mixins import ModelUserFieldPermissionMixin


class ProjectDetailView(LoginRequiredMixin,
                        ModelUserFieldPermissionMixin,
                        DetailView):
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


class ProjectUpdateView(LoginRequiredMixin,
                        ModelUserFieldPermissionMixin,
                        UpdateView):
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


class ProjectDeleteView(LoginRequiredMixin,
                        ModelUserFieldPermissionMixin,
                        DeleteView):
    model = Project
    form_class = ProjectDeleteForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        reset_selection(request=self.request, pk=(self.kwargs["pk"]))
        return super().form_valid(form)


class ProjectDeployView(LoginRequiredMixin,
                        ModelUserFieldPermissionMixin,
                        FormView):
    template_name = "project/project_deploy.html"
    form_class = ProjectDeployForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        project: Project = get_object_or_404(Project,
                                             *self.args,
                                             **self.kwargs)
        self.deploy_project(self.request.user, project, self.request.POST)
        return super().form_valid(form)

    @staticmethod
    def deploy_project(user: Any,
                       project: Project,
                       post_dict: QueryDict) -> None:
        expander = CookieCutterTemplateExpander(user, project, post_dict)
        expander.expand()


class ProjectSelectView(
        LoginRequiredMixin, ModelUserFieldPermissionMixin, BaseDetailView):
    model = Project

    def get(self, request, *args, **kwargs):
        toggle_selection(request, self.kwargs.get("pk", 0))
        return redirect(reverse_lazy("index"))


class ProjectSelectModelView(
        LoginRequiredMixin, ModelUserFieldPermissionMixin, BaseDetailView):
    model = Model

    def get(self, request, *args, **kwargs):
        toggle_model_selection(request, self.kwargs.get("pk", 0))
        return redirect(reverse_lazy("index"))


class ProjectUpdateSettingsView(LoginRequiredMixin,
                                ModelUserFieldPermissionMixin, UpdateView):

    model = ProjectSettings
    form_class = ProjectEditSettingsForm
    success_url = reverse_lazy("project_detail")
    template_name = 'project/project_settings_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateSettingsView, self).get_context_data(
            **kwargs)
        context["next_url"] = self.request.GET.get("next")  # pass `next`
        # parameter received from previous page to the context
        return context

    def get_initial(self) -> dict[str, Any]:
        if not self.object or not self.object.admin_password or self.object.admin_password == "":
            self.initial["admin_password"] = generate_random_admin_password()
            self.initial["demo_user_password"] = generate_random_admin_password()
        return super().get_initial()

    def get_success_url(self):
        set_selection(self.request, self.kwargs.get("pk", 0))
        next_url = self.request.GET.get("next")
        return next_url if next_url else reverse_lazy("index")

    # noinspection PyUnusedLocal
    def get_object(self, queryset=None):
        project: Project = \
            get_object_or_404(Project, *self.args, **self.kwargs)
        obj, created = ProjectSettings.objects.get_or_create(project=project)
        return obj

    # noinspection PyMethodMayBeStatic
    def get_user_holder(self, model_object: ProjectSettings):
        return model_object.project


class ProjectCreateModelView(LoginRequiredMixin,
                             CreateView):
    model = Model
    form_class = ProjectEditModelForm

    # noinspection PyMethodMayBeStatic
    def get_user_holder(self, model_object: Model):
        return model_object.transformation_mapping.project

    def form_valid(self, form):
        project: Project = \
            get_object_or_404(Project, *self.args, **self.kwargs)
        tm, created = TransformationMapping.objects.get_or_create(project=project)
        form.instance.transformation_mapping = tm
        return super().form_valid(form)

    def get_initial(self) -> dict[str, Any]:
        project: Project = \
            get_object_or_404(Project, *self.args, **self.kwargs)
        tm = TransformationMapping.objects.filter(project=project).get()
        if tm:
            if not self.object or not self.object.index or self.object.index == 0:
                max_ = Model.objects.filter(transformation_mapping=tm).aggregate(max=Max('index'))['max']
                if max_:
                    self.initial['index'] = max_ + 1
                    main_entity = Model.objects.filter(transformation_mapping=tm, is_main_entity=1).first()
                    self.initial['is_main_entity'] = not main_entity
                else:
                    self.initial['index'] = 1
                    self.initial['is_main_entity'] = 1

        else:
            self.initial['index'] = 1
            self.initial['is_main_entity'] = 1

        return super().get_initial()

    def get_success_url(self) -> str:
        return reverse_lazy('project_list_model', kwargs={'pk': self.object.transformation_mapping.project.id})


class ProjectUpdateModelView(LoginRequiredMixin,
                             ModelUserFieldPermissionMixin, UpdateView):
    model = Model
    form_class = ProjectEditModelForm
    success_url = reverse_lazy("project_detail")


class ProjectDeleteSettingsView(LoginRequiredMixin,
                                ModelUserFieldPermissionMixin, DeleteView):
    model = Model
    form_class = ProjectDeleteModelForm
    success_url = reverse_lazy("project_detail")


class ProjectListModelView(LoginRequiredMixin,
                           ListView):
    model = Model

    def get_queryset(self):
        if self.request.user.is_authenticated:
            project: Project = \
                get_object_or_404(Project, *self.args, **self.kwargs)

            user = self.request.user
            if not user.is_superuser and project.user != user:
                return super().handle_no_permission()

            tm = TransformationMapping.objects.filter(project=project).first()
            if tm:
                return Model.objects.filter(transformation_mapping=tm)
            else:
                return QuerySet(Model)
        else:
            return QuerySet(Model)
