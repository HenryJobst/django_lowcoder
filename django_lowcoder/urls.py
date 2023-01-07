"""django_lowcoder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.shortcuts import redirect
from django.urls import path, include, re_path

from project.admin import admin_site

from project.views.views_registration import LoginView

urlpatterns = [
    path("project/", include("project.urls")),
    path("", lambda request: redirect("project/")),
    path("accounts/login/", LoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("dlc-admin/", admin_site.urls),
    path("favicon.ico", lambda request: redirect("project/favicon.ico")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]
