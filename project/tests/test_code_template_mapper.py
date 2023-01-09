from django.test import TestCase
from slugify import slugify

from project.models import (
    Project,
    CodeTemplate,
    ProgrammingLanguage,
    CodeTemplateParameter,
    ProjectSettings,
)
from project.services.code_template_mapper import CodeTemplateMapper, Directories
from project.tests.factories import UserFactory


class TestCodeTemplateMapper(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.a_project = Project(name="A Project", description="...", user=self.user)
        self.a_project.save()
        self.a_project_settings = ProjectSettings(
            project=self.a_project, domain_name="test.org"
        )
        self.a_project_settings.save()

        self.prog_lang = ProgrammingLanguage(name="Python")
        self.prog_lang.save()
        self.code_template = CodeTemplate(
            name="Dummy", path="Dummy", programming_language=self.prog_lang
        )
        self.code_template.save()

        self.code_template_mapper: CodeTemplateMapper = CodeTemplateMapper(
            None, self.a_project, self.code_template
        )

    def test_expand_string(self):
        a_string = "a_string"
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="project_name",
            value=a_string,
        )

        assert self.code_template_mapper.expand(param) == a_string

    def test_expand_invalid(self):
        invalid_token = "{{}}"
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="a_invalid",
            value=invalid_token,
        )

        assert self.code_template_mapper.expand(param) == invalid_token

    def test_expand_none(self):
        none_value: str | None = None
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="none_value",
            value=None,
        )

        assert self.code_template_mapper.expand(param) == none_value

    def test_expand_project_name(self):
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="project_name",
            value="{{project_name}}",
        )

        assert self.code_template_mapper.expand(param) == self.a_project.name

    def test_expand_project_name_praefix_suffix(self):
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="project_name",
            value="##{{project_name}}**",
        )

        assert self.code_template_mapper.expand(param) == f"##{self.a_project.name}**"

    def test_expand_project_slug(self):
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="project_slug",
            value="{{project_slug}}",
        )

        assert self.code_template_mapper.expand(param) == slugify(self.a_project.name)

    def test_expand_project_description(self):
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="project_description",
            value="{{project_description}}",
        )

        assert self.code_template_mapper.expand(param) == self.a_project.description

    def test_expand_author_name(self):
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="author_name",
            value="{{author_name}}",
        )

        assert self.code_template_mapper.expand(param) == self.a_project.user.username

    def test_expand_project_domain_name(self):
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="project_domain_name",
            value="{{project_domain_name}}",
        )

        assert (
            self.code_template_mapper.expand(param)
            == self.a_project.projectsettings.domain_name
        )

    def test_expand_code_template_path(self):
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="template",
            value="{{code_template_path}}",
        )

        assert self.code_template_mapper.expand(param) == self.code_template.path

    def test_expand_output_directory(self):
        param = CodeTemplateParameter(
            code_template=self.code_template,
            name="output_directory",
            value="{{output_dir}}",
        )

        assert self.code_template_mapper.expand(param) == Directories().output_dir()
