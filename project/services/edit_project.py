from typing import Any

from django.http import QueryDict
from django.urls import reverse_lazy

from project.models import Project
from project.services.cookiecutter_templete_expander import CookieCutterTemplateExpander


# noinspection PyUnusedLocal
def get_projects_or_next_url(self: object, next_url: str) -> str:
    return next_url if next_url else reverse_lazy("index")


# noinspection PyUnusedLocal
def get_project_edit_or_next_url(self: object, next_url: str, pk: int) -> str:
    return next_url if next_url else reverse_lazy("project_detail", kwargs={"pk": pk})


def get_project_edit_or_next_url_p(
    self: object, next_url: str, project: Project
) -> str:
    return get_project_edit_or_next_url(self, next_url, project.id)


def deploy_project(user: Any, project: Project, post_dict: QueryDict) -> None:
    expander = CookieCutterTemplateExpander(user, project, post_dict)
    expander.expand()


def import_project(user: Any, project: Project, post_dict: QueryDict) -> None:
    pass
