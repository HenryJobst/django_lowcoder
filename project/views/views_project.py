from pathlib import Path
from typing import Any, Callable

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
    FormView,
)

from project.forms.forms_project import (
    ProjectEditForm,
    ProjectDeleteForm,
    ProjectDeployForm,
    ProjectEditSettingsForm,
    ProjectEditModelForm,
    ProjectDeleteModelForm,
    ProjectEditFieldForm,
    ProjectDeleteFieldForm,
    ProjectEditFileForm,
    ProjectDeleteFileForm,
    ProjectImportFileForm,
    var_name,
)
from project.models import (
    TransformationMapping,
    ProjectSettings,
    generate_random_admin_password,
    Field,
    TransformationFile,
)
from project.services.edit_model import (
    model_up,
    model_down,
    init_main_entity,
    init_index,
    unset_main_entity,
    set_new_main_entity,
    field_up,
    field_down,
    get_model_edit_or_next_url_p,
    get_field_edit_or_next_url_p,
    get_models_or_next_url_via_parent,
    get_fields_or_next_url_via_parent,
    get_file_edit_or_next_url_p,
)
from project.services.edit_project import (
    get_project_edit_or_next_url,
    deploy_project,
    get_projects_or_next_url,
)
from project.services.import_file import import_file
from project.services.importer import Importer
from project.services.session import *
from project.views.mixins import ModelUserFieldPermissionMixin

SHEET_PARAMS = "sheet_params"

NEXT_URL_PARAM = "next"


class NextMixin:
    url_or_next_function: Callable[[str], str] = get_projects_or_next_url
    url_or_next_function_with_pk: Callable[[str, int], str] | None = None
    url_or_next_function_with_object: Callable[[str, Project], str] | Callable[
        [str, Model], str
    ] | Callable[[str, Field], str] | None = None

    # noinspection PyUnresolvedReferences,PyArgumentList
    def get_success_url(self) -> str:
        if self.url_or_next_function_with_pk:
            return self.url_or_next_function_with_pk(
                self.request.GET.get(NEXT_URL_PARAM), self.kwargs.get("pk")
            )
        elif self.url_or_next_function_with_object:
            return self.url_or_next_function_with_object(
                self.request.GET.get(NEXT_URL_PARAM), self.object
            )
        else:
            return self.url_or_next_function(self.request.GET.get(NEXT_URL_PARAM))


class ProjectViewMixin(NextMixin):
    url_or_next_function_with_pk = get_project_edit_or_next_url


class ProjectListMixin(NextMixin):
    url_or_next_function_with_pk = get_projects_or_next_url


class ProjectSelectionMixin:
    # noinspection PyUnresolvedReferences
    def get(self, request, *args, **kwargs) -> HttpResponse:
        set_selection(self.request, self.kwargs["pk"])
        return super().get(request, *args, **kwargs)


class ProjectDetailView(
    LoginRequiredMixin,
    ProjectViewMixin,
    ModelUserFieldPermissionMixin,
    ProjectSelectionMixin,
    DetailView,
):
    model = Project


class ProjectCreateView(LoginRequiredMixin, ProjectListMixin, CreateView):
    model = Project
    form_class = ProjectEditForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        set_selection(self.request, self.object.id)
        return super().get_success_url()


class ProjectUpdateView(
    LoginRequiredMixin,
    ModelUserFieldPermissionMixin,
    ProjectViewMixin,
    ProjectSelectionMixin,
    UpdateView,
):
    model = Project
    form_class = ProjectEditForm

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next")  # pass `next`
        # parameter received from previous page to the context
        return context

    def get_success_url(self) -> str:
        set_selection(self.request, self.kwargs["pk"])
        return super().get_success_url()


class ProjectDeleteView(
    LoginRequiredMixin,
    ModelUserFieldPermissionMixin,
    NextMixin,
    ProjectSelectionMixin,
    DeleteView,
):
    model = Project
    form_class = ProjectDeleteForm

    def form_valid(self, form):
        reset_selection(request=self.request, pk=(self.kwargs["pk"]))
        return super().form_valid(form)


class ProjectDeployView(
    LoginRequiredMixin,
    ProjectListMixin,
    ModelUserFieldPermissionMixin,
    ProjectSelectionMixin,
    FormView,
):
    template_name = "project/project_deploy.html"
    form_class = ProjectDeployForm
    model = Project

    def form_valid(self, form):
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)
        deploy_project(self.request.user, project, self.request.POST)
        return super().form_valid(form)

    def get_object(self):
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)
        set_selection(self.request, project.pk)
        return project


class ProjectSelectView(
    LoginRequiredMixin, ModelUserFieldPermissionMixin, BaseDetailView
):
    model = Project

    def get(self, request, *args, **kwargs):
        toggle_selection(request, self.kwargs.get("pk", 0))
        return redirect(reverse_lazy("index"))


class ProjectUpdateSettingsView(
    LoginRequiredMixin, ModelUserFieldPermissionMixin, NextMixin, UpdateView
):

    model = ProjectSettings
    form_class = ProjectEditSettingsForm
    template_name = "project/project_settings_detail.html"
    url_or_next_function_with_pk = get_project_edit_or_next_url

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateSettingsView, self).get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next")  # pass `next`
        # parameter received from previous page to the context
        return context

    def get_initial(self) -> dict[str, Any]:
        if (
            not self.object
            or not self.object.admin_password
            or self.object.admin_password == ""
        ):
            self.initial["admin_password"] = generate_random_admin_password()
        return super().get_initial()

    # noinspection PyUnusedLocal
    def get_object(self, queryset=None):
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)
        set_selection(self.request, project.pk)
        obj, created = ProjectSettings.objects.get_or_create(project=project)
        return obj

    # noinspection PyMethodMayBeStatic
    def get_user_holder(self, model_object: ProjectSettings):
        return model_object.project


class ProjectModelViewMixin(NextMixin):
    url_or_next_function_with_object = get_model_edit_or_next_url_p

    # noinspection PyMethodMayBeStatic
    def get_user_holder(self, entity: Model | Project):
        if isinstance(entity, Project):
            return entity
        return entity.transformation_mapping.project


class ProjectFieldViewMixin(NextMixin):
    url_or_next_function_with_object = get_field_edit_or_next_url_p

    # noinspection PyMethodMayBeStatic
    def get_user_holder(self, entity: Field | Project):
        if isinstance(entity, Project):
            return entity
        return entity.model.transformation_mapping.project


class ProjectFileViewMixin(NextMixin):
    url_or_next_function_with_object = get_file_edit_or_next_url_p

    # noinspection PyMethodMayBeStatic
    def get_user_holder(self, entity: TransformationFile | Project):
        if isinstance(entity, Project):
            return entity
        return entity.transformation_mapping.project


class ProjectCreateModelView(
    LoginRequiredMixin, ProjectModelViewMixin, ModelUserFieldPermissionMixin, CreateView
):
    model = Model
    form_class = ProjectEditModelForm
    url_or_next_function_with_object = None
    url_or_next_function_with_pk = get_models_or_next_url_via_parent

    # noinspection PyUnusedLocal
    def get_object(self, **kwargs):
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)
        set_selection(self.request, project.pk)
        return project

    def form_valid(self, form):
        tm, created = TransformationMapping.objects.get_or_create(
            project=(self.get_object())
        )
        form.instance.transformation_mapping = tm
        unset_main_entity(form.instance)
        init_index(form.instance)
        return super().form_valid(form)

    def get_initial(self) -> dict[str, Any]:
        initial: dict = super().get_initial()
        initial["is_main_entity"] = init_main_entity(self.get_object())
        return initial

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["project"] = self.get_object()
        return data


class ProjectDetailModelView(
    LoginRequiredMixin, ProjectModelViewMixin, ModelUserFieldPermissionMixin, DetailView
):
    model = Model


class ProjectUpdateModelView(
    LoginRequiredMixin, ProjectModelViewMixin, ModelUserFieldPermissionMixin, UpdateView
):
    model = Model
    form_class = ProjectEditModelForm

    def form_valid(self, form) -> HttpResponse:
        unset_main_entity(self.object)
        return super().form_valid(form)


class ProjectModelUpView(
    LoginRequiredMixin, ProjectModelViewMixin, ModelUserFieldPermissionMixin, UpdateView
):
    model = Model
    fields = []
    url_or_next_function_with_object = None
    url_or_next_function_with_pk = get_models_or_next_url_via_parent

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        model_up(*args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())


class ProjectModelDownView(
    LoginRequiredMixin, ProjectModelViewMixin, ModelUserFieldPermissionMixin, UpdateView
):
    model = Model
    fields = []
    url_or_next_function_with_object = None
    url_or_next_function_with_pk = get_models_or_next_url_via_parent

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        model_down(*args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())


class ProjectDeleteModelView(
    LoginRequiredMixin, ProjectModelViewMixin, ModelUserFieldPermissionMixin, DeleteView
):
    model = Model
    form_class = ProjectDeleteModelForm

    def form_valid(self, form: ProjectDeleteModelForm) -> HttpResponse:
        set_new_main_entity(self.object)
        return super().form_valid(form)


class ProjectListModelsView(LoginRequiredMixin, ListView):
    model = Model

    def get_queryset(self):
        if self.request.user.is_authenticated:
            project: Project = get_object_or_404(Project, *self.args, **self.kwargs)
            set_selection(self.request, project.pk)
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


class ProjectSelectModelView(
    LoginRequiredMixin,
    ProjectModelViewMixin,
    ModelUserFieldPermissionMixin,
    BaseDetailView,
):
    model = Model
    url_or_next_function_with_object = None
    url_or_next_function_with_pk = get_models_or_next_url_via_parent

    def get(self, request, *args, **kwargs):
        toggle_model_selection(request, self.kwargs.get("pk", 0))
        return HttpResponseRedirect(self.get_success_url())


class ProjectListFieldsView(LoginRequiredMixin, ListView):
    model = Field

    def get_queryset(self):
        if self.request.user.is_authenticated:
            model: Model = get_object_or_404(Model, *self.args, **self.kwargs)
            set_model_selection(self.request, model.pk)

            user = self.request.user
            if (
                not user.is_superuser
                and model.transformation_mapping.project.user != user
            ):
                return super().handle_no_permission()

            return Field.objects.filter(model=model)
        else:
            return QuerySet(Field)


class ProjectCreateFieldView(
    LoginRequiredMixin, ProjectFieldViewMixin, ModelUserFieldPermissionMixin, CreateView
):
    model = Field
    form_class = ProjectEditFieldForm

    # noinspection PyUnusedLocal
    def get_object(self, **kwargs):
        model: Model = get_object_or_404(Model, *self.args, **self.kwargs)
        set_model_selection(self.request, model.pk)
        return model

    def form_valid(self, form):
        form.instance.model = self.get_object()
        init_index(form.instance)
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["model"] = self.get_object()
        return data


class ProjectUpdateFieldView(
    LoginRequiredMixin, ProjectFieldViewMixin, ModelUserFieldPermissionMixin, UpdateView
):
    model = Field
    form_class = ProjectEditFieldForm

    def form_valid(self, form) -> HttpResponse:
        return super().form_valid(form)


class ProjectFieldUpView(
    LoginRequiredMixin, ProjectFieldViewMixin, ModelUserFieldPermissionMixin, UpdateView
):
    model = Field
    fields = []
    url_or_next_function_with_object = None
    url_or_next_function_with_pk = get_fields_or_next_url_via_parent

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        field_up(*args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())


class ProjectFieldDownView(
    LoginRequiredMixin, ProjectFieldViewMixin, ModelUserFieldPermissionMixin, UpdateView
):
    model = Field
    fields = []
    url_or_next_function_with_object = None
    url_or_next_function_with_pk = get_fields_or_next_url_via_parent

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        field_down(*args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())


class ProjectDeleteFieldView(
    LoginRequiredMixin, ProjectFieldViewMixin, ModelUserFieldPermissionMixin, DeleteView
):
    model = Field
    form_class = ProjectDeleteFieldForm

    def form_valid(self, form: ProjectDeleteFieldForm) -> HttpResponse:
        return super().form_valid(form)


class ProjectListFilesView(LoginRequiredMixin, ListView):
    model = TransformationFile

    def get_queryset(self):
        if self.request.user.is_authenticated:
            project: Project = get_object_or_404(Project, *self.args, **self.kwargs)
            set_selection(self.request, project.pk)
            user = self.request.user
            if not user.is_superuser and project.user != user:
                return super().handle_no_permission()

            tm = TransformationMapping.objects.filter(project=project).first()
            if tm:
                return TransformationFile.objects.filter(transformation_mapping=tm)
            else:
                return QuerySet(TransformationFile)
        else:
            return QuerySet(TransformationFile)


class ProjectCreateFileView(
    LoginRequiredMixin, ProjectFileViewMixin, ModelUserFieldPermissionMixin, CreateView
):
    model = TransformationFile
    form_class = ProjectEditFileForm

    def get_object(self):
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)
        set_selection(self.request, project.pk)
        return project

    def form_valid(self, form):
        tm, created = TransformationMapping.objects.get_or_create(
            project=(self.get_object())
        )
        form.instance.transformation_mapping = tm
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["project"] = self.get_object()
        return data


class ProjectDeleteFileView(
    LoginRequiredMixin, ProjectFileViewMixin, ModelUserFieldPermissionMixin, DeleteView
):
    model = TransformationFile
    form_class = ProjectDeleteFileForm


class ProjectImportFileView(
    LoginRequiredMixin, ProjectFileViewMixin, ModelUserFieldPermissionMixin, FormView
):
    model = TransformationFile
    template_name = "project/project_import.html"

    def get_form(self, form_class=None):
        file: TransformationFile = self.get_object()
        importer = Importer(Path(file.file.path))
        sheet_params = self.get_session_sheet_params(importer.sheets())
        successfull, df_by_sheet = import_file(importer, sheet_params)
        assert successfull
        self.set_session_sheet_params(df_by_sheet)

        form = ProjectImportFileForm(**self.get_form_kwargs())
        form.init_helper(df_by_sheet, file.pk)
        return form

    def set_session_sheet_params(self, df_by_sheet):
        sheet_params: dict[str, Importer.SheetReaderParams] = {}
        for k, v in df_by_sheet.items():
            sheet = slugify(k)
            sheet_params[sheet] = v[1]
        self.request.session[SHEET_PARAMS] = sheet_params

    def get_session_sheet_params(
        self, sheets: list[str]
    ) -> dict[str, Importer.SheetReaderParams]:
        sheet_params = {}
        if SHEET_PARAMS in self.request.session:
            session_params = self.request.session[SHEET_PARAMS]
            for s in sheets:
                sheet = slugify(s)
                if sheet in session_params:
                    sheet_params[sheet] = session_params[sheet]
                else:
                    sheet_params[sheet] = Importer.SheetReaderParams()
                sheet_params[sheet].header = self.request.GET.get(
                    var_name(sheet, "header"), sheet_params[sheet].header
                )
        return sheet_params

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        file: TransformationFile = self.get_object()
        successfull, df_by_sheet = import_file(Importer(Path(file.file.path)))
        if successfull:
            initial["df_by_sheet"] = df_by_sheet
        return initial

    def get_object(self):
        file: TransformationFile = get_object_or_404(
            TransformationFile, *self.args, **self.kwargs
        )
        set_selection(self.request, file.transformation_mapping.project.id)
        return file

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        file: TransformationFile = self.get_object()
        successfull, df_by_sheet = import_file(Importer(Path(file.file.path)))
        if successfull:
            context["df_by_sheet"] = df_by_sheet
        return context
