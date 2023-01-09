import os
import re
from typing import Final

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from project.models import Project, CodeTemplate, CodeTemplateParameter, ProjectSettings

COOKIECUTTER_REPLAY: Final[str] = "cookiecutter_replay/"
COOKIECUTTERS: Final[str] = "cookiecutters/"
OUTPUT_DIR: Final[str] = "output/"


# noinspection PyMethodMayBeStatic
class Directories:
    def output_dir(self):
        return os.path.join(os.getcwd(), OUTPUT_DIR)

    def cookiecutters_dir(self):
        return os.path.join(os.getcwd(), os.path.join(OUTPUT_DIR, COOKIECUTTERS))

    def replay_dir(self):
        return os.path.join(os.getcwd(), os.path.join(OUTPUT_DIR, COOKIECUTTER_REPLAY))


class CodeTemplateMapper:
    def __init__(
        self, request: HttpRequest | None, project: Project, code_template: CodeTemplate
    ):
        self.request = request
        self.project: Project = project
        self.project_settings: ProjectSettings = project.projectsettings
        self.code_template: CodeTemplate = code_template
        self.directories = Directories()
        self.mappings = {
            "{{project_name}}": (Project, "name"),
            "{{project_slug}}": (Project, "slug"),
            "{{project_description}}": (Project, "description"),
            "{{author_name}}": (User, "username"),
            "{{project_domain_name}}": (ProjectSettings, "domain_name"),
            "{{project_admin_username}}": (ProjectSettings, "admin_name"),
            "{{project_admin_password}}": (ProjectSettings, "admin_password"),
            "{{project_docker_root}}": (ProjectSettings, "docker_root"),
            "{{author_email}}": (User, "email"),
            "{{code_template_path}}": (CodeTemplate, "path"),
            "{{output_dir}}": (Directories, "output_dir"),
            "{{cookiecutters_dir}}": (Directories, "cookiecutters_dir"),
            "{{replay_dir}}": (Directories, "replay_dir"),
        }

    def instance(self, clazz):
        if clazz.__name__ == "Project":
            return self.project
        elif clazz.__name__ == "ProjectSettings":
            return self.project.projectsettings
        elif clazz.__name__ == "User":
            return self.project.user
        elif clazz.__name__ == "Directories":
            return self.directories
        elif clazz.__name__ == "CodeTemplate":
            return self.code_template

    def expand(self, param: CodeTemplateParameter) -> str:

        prefix = ""
        postfix = ""
        value = param.value

        match = re.search(r"(.*)({{.+?}})(.*)", param.value)
        if match:
            prefix = match.group(1)
            value = match.group(2)
            postfix = match.group(3)

        if value in self.mappings:
            mapping_class, mapping_value = self.mappings[value]
            if (
                not mapping_class
                or not mapping_value
                or not hasattr(mapping_class, mapping_value)
            ):
                raise ValueError(
                    _(
                        "Invalid mapping for Code Template: %(ct)s, Parameter: %(param_name)s Value: %("
                        "param_value)s"
                    )
                    % {
                        "ct": self.code_template.name,
                        "param_name": param.name,
                        "param_value": param.value,
                    }
                )

            attr = getattr(self.instance(mapping_class), mapping_value)

            if callable(attr):
                return prefix + attr() + postfix
            else:
                return prefix + attr + postfix

        elif match:
            messages.add_message(
                self.request,
                messages.WARNING,
                _(
                    "No mapping found for Code Template: %(ct)s, Parameter: %(param_name)s Value: %("
                    "param_value)s"
                )
                % {
                    "ct": self.code_template.name,
                    "param_name": param.name,
                    "param_value": param.value,
                },
            )

        return param.value
