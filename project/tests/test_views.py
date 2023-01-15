from typing import Any
from unittest import skipIf
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect, QueryDict, HttpRequest
from django.test import RequestFactory, TestCase, Client

from project.tests.factories import *
from project.views.views import IndexView

pytestmark = pytest.mark.django_db


class TestIndexView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_not_authenticated(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        response = IndexView.as_view()(request)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == 302
        login_url = settings.LOGIN_URL
        assert response.url == f"{login_url}?next=/"

    def test_authenticated(self):
        request = self.factory.get("/")
        request.user = UserFactory()

        response = IndexView.as_view()(request)

        assert response.status_code == 200


class TestProjectViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)
        self.a_project = Project(name="A Project", user=self.user)
        self.a_project.save()

    def test_get_create_project(self):
        response = self.client.get("/project/create")

        assert response.status_code == 200

    def test_post_create_project(self):
        response = self.client.post(
            "/project/create", {"name": "test_name", "description": "test_description"}
        )

        self.assertRedirects(response, "/project/")

    def test_get_project_detail(self):
        response = self.client.get(f"/project/{self.a_project.pk}")
        assert response.status_code == 200

    def test_get_edit_projectsettings(self):
        response = self.client.get(f"/project/settings/{self.a_project.pk}/edit")

        assert response.status_code == 200

    def test_post_edit_projectsettings(self):
        response = self.client.post(
            f"/project/settings/{self.a_project.pk}/edit",
            {
                "project": self.a_project,
                "admin_name": "admin_name",
                "admin_password": "admin_password",
            },
        )

        assert response.status_code == 200

    def test_get_select_project(self):
        response = self.client.get(f"/project/{self.a_project.pk}/select")

        self.assertRedirects(response, "/project/")

    def test_get_edit_project(self):
        response = self.client.get(f"/project/{self.a_project.pk}/edit")

        assert response.status_code == 200

    def test_post_edit_project(self):
        response = self.client.post(
            f"/project/{self.a_project.pk}/edit",
            {"name": "test_name", "description": "test_description"},
        )

        assert response.status_code == 302
        # noinspection PyUnresolvedReferences
        assert response.url == f"/project/{self.a_project.pk}"

    @skipIf(True, "Translation not available yet.")
    def test_get_delete_project(self):
        response = self.client.get(f"/project/{self.a_project.pk}/delete")

        self.assertContains(response, "sicher", html=True)

    def test_post_delete_project(self):
        response = self.client.post(f"/project/{self.a_project.pk}/delete")

        self.assertRedirects(response, f"/project/")

    def test_get_deploy_project(self):
        response = self.client.get(f"/project/{self.a_project.pk}/deploy")
        self.assertContains(
            response, text="<legend>Projekt generieren</legend>", html=True
        )

    @staticmethod
    def mocked_deploy_project(
        request: HttpRequest, user: Any, project: Project, post_dict: QueryDict
    ) -> None:
        pass

    # noinspection PyUnusedLocal
    @patch(
        "project.services.edit_project.deploy_project",
        side_effect=mocked_deploy_project,
    )
    @skipIf(True, "Skipped until values for parameters are clear in mind")
    def test_post_deploy_project(self, mock):
        response = self.client.post(
            f"/project/{self.a_project.pk}/deploy",
            {"app_type": 0, "deploy_type": 0},
        )

        self.assertRedirects(response, "/project/")

    def test_get_field_detail(self):
        field = FieldFactory()
        self.client.force_login(field.model.transformation_mapping.project.user)
        response = self.client.get(f"/project/field/{field.pk}/edit")
        assert response.status_code == 200
