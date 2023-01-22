from pathlib import Path
from shutil import make_archive
from typing import Any

from django.contrib import messages
from django.conf import settings
from django.http import QueryDict, HttpRequest
from django.db import models
from django.utils.translation import gettext_lazy as _
from slugify import slugify

from project.models import (
    Project,
    CodeTemplate,
    TransformationMapping,
    deployed_archive_user_directory_path,
)
from project.services.cookiecutter_template_expander import CookieCutterTemplateExpander
from project.services.model_exporter import ModelExporter
from project.services.model_exporter_django import ModelExporterDjango
from project.services.model_exporter_jpa import ModelExporterJpa


def prepare_deploy_project(
    request: HttpRequest, user: Any, project: Project, post_dict: QueryDict
) -> CookieCutterTemplateExpander:
    return CookieCutterTemplateExpander(request, user, project, post_dict)


def deploy_project(
    cookiecutter_template_expander: CookieCutterTemplateExpander,
) -> str:
    cookiecutter_template_expander.expand()

    model_exporter: ModelExporter | None = None
    if (
        cookiecutter_template_expander.config.code_template.model_exporter
        == CodeTemplate.ModelExporterClass.JPA
    ):
        model_exporter = ModelExporterJpa(cookiecutter_template_expander)
    elif (
        cookiecutter_template_expander.config.code_template.model_exporter
        == CodeTemplate.ModelExporterClass.DJANGO
    ):
        model_exporter = ModelExporterDjango(cookiecutter_template_expander)
    else:
        messages.add_message(
            cookiecutter_template_expander.request,
            messages.WARNING,
            _(
                "No ModelExpander class for the given programming language available! Contact support "
                "for further help."
            ),
        )

    if model_exporter:
        project_path = model_exporter.export()
        project: Project = cookiecutter_template_expander.config.project
        tm: TransformationMapping = project.transformationmapping
        project_zip_file = Path(settings.MEDIA_ROOT).joinpath(
            deployed_archive_user_directory_path(tm, project.slug())
        )
        archive = make_archive(str(project_zip_file), "zip", project_path)
        tm.deployed_archive.name = str(project_zip_file) + ".zip"
        tm.save()
        return archive
