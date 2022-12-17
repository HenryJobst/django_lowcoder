from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/settings', views.ProjectSettingsView.as_view(),
         name='project_settings'),
    path('accounts/register', views.RegisterView.as_view(), name='register'),
    path('accounts/login', views.LoginView.as_view(), name='login'),
]

