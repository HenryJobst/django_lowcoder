import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse

from project.tests.factories import UserFactory
from project.views.views import IndexView

pytestmark = pytest.mark.django_db


class TestIndexView:
    def test_authenticated(self, rf: RequestFactory):
        request = rf.get("/")
        request.user = UserFactory()

        response = IndexView.as_view()(request)
        assert response.status_code == 200

    def test_not_authenticated(self, rf: RequestFactory):
        request = rf.get("/")
        request.user = AnonymousUser()

        response = IndexView.as_view()(request)
        login_url = settings.LOGIN_URL

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == 302
        assert response.url == f"{login_url}?next=/"
