from django.urls import path

from project.views import views
from project.views.views_project import *

from project.views.views_registration import RegisterView
from project.views.views import IndexView, favicon

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("favicon.ico", favicon),
    path("<int:pk>", ProjectDetailView.as_view(), name="project_detail"),
    path("create", ProjectCreateView.as_view(), name="project_create"),
    path("<int:pk>/select", ProjectSelectView.as_view(), name="project_select"),
    path("<int:pk>/edit", ProjectUpdateView.as_view(), name="project_update"),
    path("<int:pk>/delete", ProjectDeleteView.as_view(), name="project_delete"),
    path("<int:pk>/deploy", ProjectDeployView.as_view(), name="project_deploy"),
    path(
        "<int:pk>/download",
        ProjectDeployResultView.as_view(),
        name="project_deploy_result",
    ),
    path("accounts/register", RegisterView.as_view(), name="register"),
    path(
        "settings/<int:pk>/edit",
        ProjectUpdateSettingsView.as_view(),
        name="project_update_settings",
    ),
    path(
        "<int:pk>/models", ProjectListModelsView.as_view(), name="project_list_models"
    ),
    path(
        "<int:pk>/model/create",
        ProjectCreateModelView.as_view(),
        name="project_create_model",
    ),
    path(
        "model/<int:pk>",
        ProjectDetailModelView.as_view(),
        name="project_detail_model",
    ),
    path(
        "model/<int:pk>/edit",
        ProjectUpdateModelView.as_view(),
        name="project_update_model",
    ),
    path(
        "model/<int:pk>/delete",
        ProjectDeleteModelView.as_view(),
        name="project_delete_model",
    ),
    path(
        "model/<int:pk>/select",
        ProjectSelectModelView.as_view(),
        name="project_select_model",
    ),
    path(
        "model/<int:pk>/up",
        ProjectModelUpView.as_view(),
        name="project_model_up",
    ),
    path(
        "model/<int:pk>/down",
        ProjectModelDownView.as_view(),
        name="project_model_down",
    ),
    path(
        "<int:pk>/fields", ProjectListFieldsView.as_view(), name="project_list_fields"
    ),
    path(
        "<int:pk>/field/create",
        ProjectCreateFieldView.as_view(),
        name="project_create_field",
    ),
    path(
        "field/<int:pk>/edit",
        ProjectUpdateFieldView.as_view(),
        name="project_update_field",
    ),
    path(
        "field/<int:pk>/delete",
        ProjectDeleteFieldView.as_view(),
        name="project_delete_field",
    ),
    path(
        "field/<int:pk>/up",
        ProjectFieldUpView.as_view(),
        name="project_field_up",
    ),
    path(
        "field/<int:pk>/down",
        ProjectFieldDownView.as_view(),
        name="project_field_down",
    ),
    path("<int:pk>/files", ProjectListFilesView.as_view(), name="project_list_files"),
    path(
        "<int:pk>/file/create",
        ProjectCreateFileView.as_view(),
        name="project_create_file",
    ),
    path(
        "file/<int:pk>/delete",
        ProjectDeleteFileView.as_view(),
        name="project_delete_file",
    ),
    path(
        "file/<int:pk>/import",
        ProjectImportFileView.as_view(),
        name="project_import_file",
    ),
]
