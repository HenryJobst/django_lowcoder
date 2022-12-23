import json
import logging
import os
from dataclasses import dataclass
from typing import Any

import slugify
from cookiecutter.main import cookiecutter
from django.contrib.auth.models import User
from django.http import QueryDict

from project.models import Project

# from fs.memoryfs import MemoryFS

logger = logging.getLogger(__name__)


class CookiecutterConfig:
    filename = os.path.join(
        os.getcwd(), "output/config/cookiecutter-django/config.json"
    )
    config = None
    extra_context = None

    def __init__(self, user: User, project: Project, post_dict: QueryDict):
        self.user: User = user
        self.project: Project = project
        self.post_dict: QueryDict = post_dict
        self.create_config()

    def create_config(self) -> None:
        project: Project = self.project
        self.config = {
            "project_name": project.name,
            "project_slug": slugify.slugify(project.name),
            "description": project.description,
            "author_name": self.user.first_name + " " + self.user.last_name,
            "domain_name": project.project_settings.domain_name
            if hasattr(project, "project_settings")
            else "domain.de",
            "email": self.user.email,
            "version": "0.0.1",
            "open_source_license": "Not open source",
            "timezone": "UTC",
            "windows": "n",
            "use_pycharm": "n",
            "use_docker": "y" if self.post_dict["type"] == "1" else "n",
            "django_port": "8001",
            "postgresql_version": "14",
            "cloud_provider": "None",
            "mail_service": "Other SMTP",
            "use_async": "n",
            "use_drf": "n",
            "frontend_pipeline": "None",
            "use_celery": "n",
            "use_mailhog": "y",
            "use_sentry": "n",
            "use_whitenoise": "y",
            "use_heroku": "n",
            "ci_tool": "Gitlab",
            "keep_local_envs_in_vcs": "y",
            "debug": "n",
            "_template": "gh:cookiecutter/cookiecutter-django",
            "_output_dir": os.path.join(os.getcwd(), "output/"),
            "cookiecutters_dir": os.path.join(os.getcwd(), "output/cookiecutters/"),
            "replay_dir": os.path.join(os.getcwd(), "output/cookiecutter_replay/"),
        }

        with open(self.filename, "w") as f:
            f.write(json.dumps(self.config, sort_keys=False))


@dataclass
class ExpanderParameters:
    # for the meaning of the parameters see:
    # https://cookiecutter.readthedocs.io/en/stable/cookiecutter.html#module
    # -cookiecutter.main
    template: str = "https://github.com/HenryJobst/cookiecutter-django.git"
    checkout: str | None = None
    no_input: bool = True
    extra_context: dict[Any, Any] | None = None
    replay: bool = False
    overwrite_if_exists: bool = True
    output_dir: str = "output/"
    config_file: str | None = None
    default_config: bool = False
    password: str | None = None
    directory: str | None = None
    skip_if_file_exists: bool = False
    accept_hooks: bool = True


class CookieCutterTemplateExpander:
    def __init__(self, user: User, project: Project, post_dict: QueryDict):
        self.user = user
        self.project = project
        self.post_dict = post_dict
        # self.mem_fs = MemoryFS()
        # self.home_fs = self.mem_fs.makedir("~", recreate=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        # self.mem_fs.close()

    def expand(self):
        config = self.create_config()
        expand_parameter = ExpanderParameters()
        expand_parameter.config_file = config.filename
        expand_parameter.overwrite_if_exists = True
        expand_parameter.extra_context = config.config
        CookieCutterTemplateExpander._expand(expand_parameter)

    @staticmethod
    def _expand(params: ExpanderParameters):
        # os.environ.setdefault('', '')
        # Create expanded template
        cookiecutter(
            params.template,
            checkout=params.checkout,
            no_input=params.no_input,
            extra_context=params.extra_context,
            replay=params.replay,
            overwrite_if_exists=params.overwrite_if_exists,
            output_dir=params.output_dir,
            config_file=params.config_file,
            default_config=params.default_config,
            password=params.password,
            directory=params.directory,
            skip_if_file_exists=params.skip_if_file_exists,
            accept_hooks=params.accept_hooks,
        )

    def create_config(self) -> CookiecutterConfig:
        config = CookiecutterConfig(self.user, self.project, self.post_dict)
        return config
