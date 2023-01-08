import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Final

import slugify
from cookiecutter.main import cookiecutter  # type: ignore
from django.contrib.auth.models import User
from django.http import QueryDict

from project.models import Project, CodeTemplate

COOKIECUTTER_REPLAY_ = "cookiecutter_replay/"

COOKIECUTTERS_ = "cookiecutters/"

OUTPUT_DIR: Final[str] = "output/"

# from fs.memoryfs import MemoryFS

logger = logging.getLogger(__name__)


class CookiecutterConfig:
    def get_filename(self):
        return os.path.join(
            os.getcwd(), os.path.join(OUTPUT_DIR, self.config_json_path)
        )

    config = None
    extra_context = None

    def __init__(self, user: User, project: Project, post_dict: QueryDict):
        self.user: User = user
        self.project: Project = project
        self.post_dict: QueryDict = post_dict
        self.code_template: CodeTemplate = CodeTemplate.objects.get(
            pk=self.post_dict.get("app_type")
        )
        self.programming_language = self.code_template.programming_language.name
        self.init_cookiecutter_template_config(self.code_template.pk)

    def init_cookiecutter_template_config(self, pk: int):
        if pk == 1:  # Java-Template
            self.init_cookiecutter_java_config()
        elif pk == 2:  # Django-Template
            self.init_cookiecutter_django_config()

        self.config_json_path = (
            f"config/cookiecutter-{self.code_template.pk}/config.json"
        )

        with open(self.get_filename(), "w+") as f:
            f.write(json.dumps(self.config, sort_keys=False))

    def init_cookiecutter_java_config(self):
        # TODO: move the cookiecutter template parameters to the code template table entry
        # for the values define some fixed placeholders which will be filled here with project settings
        project: Project = self.project  # type: ignore
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
            "use_intellij": "n",
            "use_docker": "y" if self.post_dict["deploy_type"] == "2" else "n",
            "exposed_port": "8001",
            "postgresql_version": "14",
            "cloud_provider": "None",
            "mail_service": "Other SMTP",
            "frontend_pipeline": "None",
            "use_mailhog": "y",
            "ci_tool": "Gitlab",
            "keep_local_envs_in_vcs": "y",
            "debug": "n",
            "_template": self.code_template.path,
            "_output_dir": os.path.join(os.getcwd(), OUTPUT_DIR),
            "cookiecutters_dir": os.path.join(
                os.getcwd(), os.path.join(OUTPUT_DIR, COOKIECUTTERS_)
            ),
            "replay_dir": os.path.join(
                os.getcwd(), os.path.join(OUTPUT_DIR, COOKIECUTTER_REPLAY_)
            ),
        }

    def init_cookiecutter_django_config(self) -> None:
        # TODO: move the cookiecutter template parameters to the code template table entry
        # for the values define some fixed placeholders which will be filled here with project settings
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
            "use_docker": "y" if self.post_dict["deploy_type"] == "2" else "n",
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
            "_output_dir": os.path.join(os.getcwd(), OUTPUT_DIR),
            "cookiecutters_dir": os.path.join(
                os.getcwd(), os.path.join(OUTPUT_DIR, COOKIECUTTERS_)
            ),
            "replay_dir": os.path.join(
                os.getcwd(), os.path.join(OUTPUT_DIR, COOKIECUTTER_REPLAY_)
            ),
        }


@dataclass
class ExpanderParameters:
    # for the meaning of the parameters see:
    # https://cookiecutter.readthedocs.io/en/stable/cookiecutter.html#module
    template: str | None = None
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

    def __init__(self, template, config_file, overwrite_if_exists, extra_context):
        self.template = template
        self.config_file = config_file
        self.overwrite_if_exists = overwrite_if_exists
        self.extra_context = extra_context


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
        expand_parameter = ExpanderParameters(
            template=config.code_template.path,
            config_file=config.get_filename(),
            overwrite_if_exists=True,
            extra_context=config.config,
        )
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
        return CookiecutterConfig(self.user, self.project, self.post_dict)
