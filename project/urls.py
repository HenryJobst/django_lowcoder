from django.urls import path

from project.views.views_project import (
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    ProjectDeployView,
    ProjectSelectView,
    ProjectUpdateSettingsView,
    ProjectCreateModelView,
    ProjectUpdateModelView,
    ProjectDeleteSettingsView,
    ProjectListModelView,
    ProjectSelectModelView,
    ProjectModelUpView,
    ProjectModelDownView,
)
from project.views.views_registration import LoginView, RegisterView
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
    path("accounts/register", RegisterView.as_view(), name="register"),
    path("accounts/login", LoginView.as_view(), name="login"),
    path(
        "settings/<int:pk>/edit",
        ProjectUpdateSettingsView.as_view(),
        name="project_update_settings",
    ),
    path("<int:pk>/model", ProjectListModelView.as_view(), name="project_list_model"),
    path(
        "<int:pk>/model/create",
        ProjectCreateModelView.as_view(),
        name="project_create_model",
    ),
    path(
        "model/<int:pk>/edit",
        ProjectUpdateModelView.as_view(),
        name="project_update_model",
    ),
    path(
        "model/<int:pk>/delete",
        ProjectDeleteSettingsView.as_view(),
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
]
