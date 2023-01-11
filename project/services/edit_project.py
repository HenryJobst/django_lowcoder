from typing import Any

from django.http import QueryDict, HttpRequest

from project.models import Project
from project.services.cookiecutter_template_expander import CookieCutterTemplateExpander


def prepare_deploy_project(
    request: HttpRequest, user: Any, project: Project, post_dict: QueryDict
) -> CookieCutterTemplateExpander:
    return CookieCutterTemplateExpander(request, user, project, post_dict)
