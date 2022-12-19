from django.urls import path

from project.views.views_project import ProjectDetailView, ProjectCreateView, \
    ProjectUpdateView, ProjectDeleteView, ProjectDeployView
from project.views.views_registration import LoginView, RegisterView
from project.views.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('<int:pk>', ProjectDetailView.as_view(), name='project_detail'),
    path('create', ProjectCreateView.as_view(),
         name='project_create'),
    path('<int:pk>/edit', ProjectUpdateView.as_view(),
         name='project_update'),
    path('<int:pk>/delete', ProjectDeleteView.as_view(),
         name='project_delete'),
    path('<int:pk>/deploy', ProjectDeployView.as_view(),
         name='project_deploy'),
    path('accounts/register', RegisterView.as_view(), name='register'),
    path('accounts/login', LoginView.as_view(), name='login'),
    ]
