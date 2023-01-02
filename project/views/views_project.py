from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    TypeVar,
    Optional,
    List,
    Tuple,
)

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
from pandas import DataFrame

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
)
from project.services.edit_project import (
    deploy_project,
)
from project.services.import_file import import_file
from project.services.importer import (
    Importer,
    SheetReaderParams,
    READ_PARAM_HEADER,
    READ_PARAM_USECOLS,
    READ_PARAM_INDEX_COL,
    READ_PARAM_NROWS,
    READ_PARAM_SKIPROWS,
    READ_PARAM_SKIPFOOTER,
    TABLE_PARAM_HEAD_ROWS,
    TABLE_PARAM_TAIL_ROWS,
    convert_param,
    create_models,
)
from project.services.session import *
from project.views.mixins import ModelUserFieldPermissionMixin

SHEET_PARAMS = "sheet_params"
NEXT_URL_PARAM = "next"


# noinspection PyUnusedLocal
def get_projects_or_next_url(next_url: str | None) -> Any:
    return next_url if next_url else reverse_lazy("index")


# noinspection PyUnusedLocal
def get_project_edit_or_next_url(next_url: str | None, pk: int) -> Any:
    return next_url if next_url else reverse_lazy("project_detail", kwargs={"pk": pk})


def get_project_edit_or_next_url_p(next_url: str | None, project: Project) -> Any:
    return get_project_edit_or_next_url(next_url, project.pk)


def get_models_or_next_url(next_url: str | None, project_pk: int) -> Any:
    return (
        next_url
        if next_url
        else reverse_lazy("project_list_models", kwargs={"pk": project_pk})
    )


def get_models_or_next_url_via_parent(next_url: str | None, model_pk: int) -> Any:
    model: Model = Model.objects.get(pk=model_pk)
    return (
        next_url
        if next_url
        else reverse_lazy(
            "project_list_models",
            kwargs={"pk": model.transformation_mapping.project.id},
        )
    )


# noinspection PyUnusedLocal
def get_model_edit_or_next_url(next_url: str | None, pk: int) -> Any:
    return (
        next_url
        if next_url
        else reverse_lazy("project_detail_model", kwargs={"pk": pk})
    )


# noinspection PyUnresolvedReferences,PyUnusedLocal
def get_model_edit_or_next_url_p(self, next_url: str | None, model: Model) -> Any:
    return get_model_edit_or_next_url(next_url, model.pk)


# noinspection PyUnusedLocal
def get_fields_or_next_url(next_url: str | None, model_pk: int) -> Any:
    return (
        next_url
        if next_url
        else reverse_lazy("project_list_fields", kwargs={"pk": model_pk})
    )


# noinspection PyUnusedLocal
def get_fields_or_next_url_via_parent(next_url: str | None, field_pk: int) -> Any:
    field: Field = Field.objects.get(pk=field_pk)
    return (
        next_url
        if next_url
        else reverse_lazy("project_list_fields", kwargs={"pk": field.model.id})
    )


# noinspection PyUnusedLocal
def get_field_edit_or_next_url(next_url: str | None, pk: int) -> Any:
    return (
        next_url
        if next_url
        else reverse_lazy("project_update_field", kwargs={"pk": pk})
    )


# noinspection PyUnresolvedReferences,PyUnusedLocal
def get_field_edit_or_next_url_p(self, next_url: str | None, field: Field) -> Any:
    return get_model_edit_or_next_url(next_url, field.pk)


# noinspection PyUnresolvedReferences,PyUnusedLocal
def get_file_edit_or_next_url_p(
    self, next_url: str | None, file: TransformationFile
) -> Any:
    return get_files_or_next_url_via_parent(next_url, file.pk)


# noinspection PyUnusedLocal
def get_files_or_next_url_via_parent(next_url: str | None, file_pk: int) -> Any:
    file: TransformationFile = TransformationFile.objects.get(pk=file_pk)
    return (
        next_url
        if next_url
        else reverse_lazy(
            "project_list_files",
            kwargs={"pk": file.transformation_mapping.project.id},
        )
    )


ET = TypeVar("ET")


class NextMixin(Generic[ET]):
    url_or_next_function: ClassVar[
        Callable[[str | None], Any]
    ] = get_projects_or_next_url
    url_or_next_function_with_pk: ClassVar[
        Callable[[str | None, int], Any] | None
    ] = None
    url_or_next_function_with_object: Optional[
        Callable[[Any, str | None, ET], Any]
    ] = None

    request: HttpRequest  # forward decl
    kwargs: dict[str, Any]  # forward decl
    get_object: Any  # forward decl

    # noinspection PyUnresolvedReferences,PyArgumentList
    def get_success_url(self) -> Any:
        next_url: str | None = self.request.GET.get(NEXT_URL_PARAM)
        if NextMixin[ET].url_or_next_function_with_pk:
            return NextMixin[ET].url_or_next_function_with_pk(  # type: ignore
                next_url, self.kwargs.get("pk", 0)
            )
        elif self.url_or_next_function_with_object:
            return self.url_or_next_function_with_object(  # type: ignore
                next_url, self.object if hasattr(self, "object") else self.get_object()
            )
            # type: ignore
        else:
            return NextMixin[ET].url_or_next_function(next_url)


class ProjectViewMixin(NextMixin):
    url_or_next_function_with_pk: ClassVar[
        Callable[[str | None, int], Any] | None
    ] = get_project_edit_or_next_url


class ProjectListMixin(NextMixin):
    pass


class ProjectSelectionMixin:

    request: HttpRequest  # forward decl
    kwargs: dict[str, Any]  # forward decl

    # noinspection PyUnresolvedReferences
    def get(self, request, *args, **kwargs) -> HttpResponse:
        set_selection(self.request, self.kwargs["pk"])
        return super().get(request, *args, **kwargs)  # type: ignore


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


class ProjectDeleteView(  # type: ignore
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
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)  # type: ignore
        deploy_project(self.request.user, project, self.request.POST)
        return super().form_valid(form)

    def get_object(self):
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)  # type: ignore
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
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)  # type: ignore
        set_selection(self.request, project.pk)
        obj, created = ProjectSettings.objects.get_or_create(project=project)
        return obj

    # noinspection PyMethodMayBeStatic
    def get_user_holder(self, model_object: ProjectSettings):
        return model_object.project


class ProjectModelViewMixin(NextMixin[Model]):
    url_or_next_function_with_object: Optional[
        Callable[[Any, str | None, Model], Any]
    ] = get_model_edit_or_next_url_p

    # noinspection PyMethodMayBeStatic

    def get_user_holder(self, entity: Model | Project) -> Project:
        if isinstance(entity, Project):
            return entity
        return entity.transformation_mapping.project


class ProjectFieldViewMixin(NextMixin[Field]):
    url_or_next_function_with_object: Optional[
        Callable[[Any, str | None, Field], Any]
    ] = get_field_edit_or_next_url_p

    # noinspection PyMethodMayBeStatic
    def get_user_holder(self, entity: Field | Project):
        if isinstance(entity, Project):
            return entity
        return entity.model.transformation_mapping.project


class ProjectFileViewMixin(NextMixin[TransformationFile]):
    url_or_next_function_with_object: Optional[
        Callable[[Any, str | None, TransformationFile], Any]
    ] = get_file_edit_or_next_url_p

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
    url_or_next_function_with_pk = get_models_or_next_url_via_parent
    url_or_next_function_with_object = None

    # noinspection PyUnusedLocal
    def get_object(self, **kwargs):
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)  # type: ignore
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


class ProjectDeleteModelView(  # type: ignore
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
            project: Project = get_object_or_404(Project, *self.args, **self.kwargs)  # type: ignore
            set_selection(self.request, project.pk)
            user = self.request.user
            if not user.is_superuser and project.user != user:
                return super().handle_no_permission()

            tm = TransformationMapping.objects.filter(project=project).first()
            if tm:
                return Model.objects.filter(transformation_mapping=tm)
            else:
                return QuerySet(Model).none()
        else:
            return QuerySet(Model).none()


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
            model: Model = get_object_or_404(Model, *self.args, **self.kwargs)  # type: ignore
            set_model_selection(self.request, model.pk)

            user = self.request.user
            if (
                not user.is_superuser
                and model.transformation_mapping.project.user != user
            ):
                return super().handle_no_permission()

            return Field.objects.filter(model=model)
        else:
            return QuerySet(Field).none()


class ProjectCreateFieldView(
    LoginRequiredMixin, ProjectFieldViewMixin, ModelUserFieldPermissionMixin, CreateView
):
    model = Field
    form_class = ProjectEditFieldForm

    # noinspection PyUnusedLocal
    def get_object(self, **kwargs):
        model: Model = get_object_or_404(Model, *self.args, **self.kwargs)  # type: ignore
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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        field: Field = get_object_or_404(Field, *self.args, **self.kwargs)  # type: ignore
        data["model"] = field.model
        return data


class ProjectFieldUpView(
    LoginRequiredMixin, ProjectFieldViewMixin, ModelUserFieldPermissionMixin, UpdateView
):
    model = Field
    fields = []
    url_or_next_function_with_pk = get_fields_or_next_url_via_parent
    url_or_next_function_with_object: Optional[
        Callable[[Any, str | None, Field], Any]
    ] = None

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        field_up(*args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())


class ProjectFieldDownView(
    LoginRequiredMixin, ProjectFieldViewMixin, ModelUserFieldPermissionMixin, UpdateView
):
    model = Field
    fields = []
    url_or_next_function_with_pk = get_fields_or_next_url_via_parent
    url_or_next_function_with_object = None

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        field_down(*args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())


class ProjectDeleteFieldView(  # type: ignore
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
            project: Project = get_object_or_404(Project, *self.args, **self.kwargs)  # type: ignore
            set_selection(self.request, project.pk)
            user = self.request.user
            if not user.is_superuser and project.user != user:
                return super().handle_no_permission()

            tm = TransformationMapping.objects.filter(project=project).first()
            if tm:
                return TransformationFile.objects.filter(transformation_mapping=tm)
            else:
                return QuerySet(TransformationFile).none()
        else:
            return QuerySet(TransformationFile).none()


class ProjectCreateFileView(
    LoginRequiredMixin, ProjectFileViewMixin, ModelUserFieldPermissionMixin, CreateView
):

    model = TransformationFile
    form_class = ProjectEditFileForm

    # noinspection PyUnusedLocal
    def get_object(self, **kwargs):
        project: Project = get_object_or_404(Project, *self.args, **self.kwargs)  # type: ignore
        set_selection(self.request, project.pk)
        return project

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST":
            tm, created = TransformationMapping.objects.get_or_create(
                project=(self.get_object())
            )
            kwargs["instance"] = TransformationFile(transformation_mapping=tm)
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        if self.request.method == "POST":
            tm, created = TransformationMapping.objects.get_or_create(
                project=(self.get_object())
            )
            initial["transformation_mapping"] = tm
        return initial

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["project"] = self.get_object()
        return data


class ProjectDeleteFileView(  # type: ignore
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
        file: TransformationFile = self.get_object()  # type: ignore
        df_by_sheet, importer = self.get_df_by_sheet(file)

        form = ProjectImportFileForm(**self.get_form_kwargs())
        form.init_helper(df_by_sheet, file.pk)

        return form

    def get_df_by_sheet(
        self, file: TransformationFile
    ) -> Tuple[Dict[str | int, Tuple[DataFrame, SheetReaderParams]], Importer]:
        importer = Importer(Path(file.file.path))
        sheet_params: Dict[
            str | int, SheetReaderParams
        ] = self.get_session_sheet_params(importer.sheets())
        successfull, df_by_sheet = import_file(importer, sheet_params)
        assert successfull
        self.set_session_sheet_params(df_by_sheet)
        return df_by_sheet, importer

    def set_session_sheet_params(self, df_by_sheet):
        sheet_params: dict[str, SheetReaderParams] = {}  # type: ignore
        for k, v in df_by_sheet.items():
            sheet = slugify(k)
            sheet_params[sheet] = v[1]
        self.request.session[SHEET_PARAMS] = sheet_params

    def get_session_sheet_params(
        self, sheets: List[str | int]
    ) -> Dict[str | int, SheetReaderParams]:
        sheet_params: Dict[str | int, SheetReaderParams] = {}
        if SHEET_PARAMS in self.request.session:
            session_params = self.request.session[SHEET_PARAMS]
            s: str | int
            for s in sheets:
                sheet: str | int
                if isinstance(s, str):
                    sheet = slugify(s)
                else:
                    sheet = s

                if sheet in session_params:
                    sheet_params[sheet] = session_params[sheet]
                else:
                    sheet_params[sheet] = SheetReaderParams()

                sheet_params = self.set_param(sheet_params, sheet, READ_PARAM_HEADER)
                sheet_params = self.set_param(sheet_params, sheet, READ_PARAM_INDEX_COL)
                sheet_params = self.set_param(sheet_params, sheet, READ_PARAM_NROWS)
                sheet_params = self.set_param(
                    sheet_params, sheet, READ_PARAM_SKIPFOOTER
                )
                sheet_params = self.set_param(sheet_params, sheet, READ_PARAM_SKIPROWS)
                sheet_params = self.set_param(sheet_params, sheet, READ_PARAM_USECOLS)
                sheet_params = self.set_param(
                    sheet_params, sheet, TABLE_PARAM_HEAD_ROWS
                )
                sheet_params = self.set_param(
                    sheet_params, sheet, TABLE_PARAM_TAIL_ROWS
                )

        return sheet_params

    def set_param(self, sheet_params, sheet, param):
        local_sheet_params = sheet_params
        form_value = self.request.GET.get(
            var_name(sheet, param), local_sheet_params[sheet].get(param)
        )
        local_sheet_params[sheet][param] = convert_param(param, form_value)
        return local_sheet_params

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse:
        file: TransformationFile = self.get_object()
        df_by_sheet: Dict[str | int, Tuple[DataFrame, SheetReaderParams]]
        importer: Importer
        df_by_sheet, importer = self.get_df_by_sheet(file)
        clean_existing_models = True
        create_models(self.request, file, df_by_sheet, clean_existing_models)
        return super().form_valid(form)

    def get_object(self):
        file: TransformationFile = get_object_or_404(  # type: ignore
            TransformationFile, *self.args, **self.kwargs
        )
        set_selection(self.request, file.transformation_mapping.project.id)
        return file
