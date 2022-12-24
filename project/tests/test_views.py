import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse

from project.tests.factories import UserFactory
from project.views.views_project import ProjectDetailView

pytestmark = pytest.mark.django_db


class TestProjectDetailView:
    @pytest.mark.skip(reason="not working because of missing custom user etc.")
    def test_authenticated(self, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = UserFactory()

        response = ProjectDetailView().as_view()

        assert response.status_code == 200

    @pytest.mark.skip(reason="not working because of missing custom user etc.")
    def test_not_authenticated(self, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()

        response = ProjectDetailView().as_view()
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == 302
        assert response.url == f"{login_url}?next=/fake-url/"
