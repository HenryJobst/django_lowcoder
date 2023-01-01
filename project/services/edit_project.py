from typing import Any

from django.http import QueryDict

from project.models import Project
from project.services.cookiecutter_templete_expander import CookieCutterTemplateExpander


def deploy_project(user: Any, project: Project, post_dict: QueryDict) -> None:
    expander = CookieCutterTemplateExpander(user, project, post_dict)
    expander.expand()
