from pathlib import Path
from typing import List
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import (
    MinLengthValidator,
    MinValueValidator,
    BaseValidator,
    FileExtensionValidator,
)
from django.db import models
from django.db.models.signals import post_delete
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from slugify import slugify

MIN_PASSWORD_LENGTH = 6

MIN_PROJECT_NAME_LENGTH = 4
MAX_PROJECT_NAME_LENGTH = 100

MIN_USER_NAME_LENGTH = 4
MIN_MODEL_NAME_LENGTH = 3
MIN_FIELD_NAME_LENGTH = 2
MIN_NAME_COMMON_LENGTH = 4

VALID_SUFFIXES = ["csv", "odf", "xls", "xlsx"]
VALID_MIMETYPES = [
    "text/csv",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]


# noinspection PyProtectedMember,PyBroadException
def file_cleanup(sender, **kwargs):
    """
    File cleanup callback used to emulate the old delete
    behavior using signals. Initially django deleted linked
    files when an object containing a File/ImageField was deleted.

    Usage:
    >>> from django.db.models.signals import post_delete
    >>> post_delete.connect(file_cleanup, sender=TransformationFile, dispatch_uid="transformation_file.file_cleanup")
    """
    for field in sender._meta.get_fields():
        if not isinstance(field, models.FileField):
            continue
        instance = kwargs["instance"]
        f = getattr(instance, field.name)
        m = instance.__class__._default_manager
        if (
            hasattr(f, "path")
            and Path(f.path).exists()
            and not m.filter(
                **{"%s__exact" % field.name: getattr(instance, field.name)}
            ).exclude(pk=instance._get_pk_val())
        ):
            try:
                default_storage.delete(f.path)
            except:
                pass


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)  # type: ignore
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)  # type: ignore

    class Meta:
        abstract = True


class ProgrammingLanguage(models.Model):
    class Meta:
        verbose_name = _("Programming Language")
        verbose_name_plural = _("Programming Languages")

    name = models.CharField(  # type: ignore
        _("programming language"),
        max_length=60,
        null=False,
        blank=False,
        validators=[MinLengthValidator(1)],
        unique=True,
    )

    def __str__(self):
        return _("Programming Language: %(name)s") % {"name": self.name}


class CodeTemplate(models.Model):
    class Meta:
        verbose_name = _("Code Template")
        verbose_name_plural = _("Code Templates")

    name = models.CharField(  # type: ignore
        _("name"),
        max_length=60,
        null=False,
        blank=False,
        validators=[MinLengthValidator(MIN_NAME_COMMON_LENGTH)],
        unique=True,
    )
    path = models.CharField(  # type: ignore
        _("path"),
        max_length=200,
        null=False,
        blank=False,
        validators=[MinLengthValidator(MIN_NAME_COMMON_LENGTH)],
        unique=True,
    )
    programming_language = models.ForeignKey(  # type: ignore
        ProgrammingLanguage,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="programming_languages",
        verbose_name=_("Programming Language"),
    )

    class ModelExporterClass(models.IntegerChoices):
        JPA = (
            1,
            _("Java JPA Entities"),
        )
        DJANGO = (
            2,
            _("Python Django Models"),
        )

    model_exporter = models.IntegerField(  # type: ignore
        _("model exporter type"),
        null=False,
        blank=False,
        # Model export types
        choices=ModelExporterClass.choices,
    )

    parameters: models.QuerySet["CodeTemplateParameter"]  # forward decl for mypy

    def __str__(self):
        return _("Code Template: %(name)s - %(lang)s - %(path)s") % {
            "name": self.name,
            "lang": self.programming_language.name,
            "path": self.path,
        }


class CodeTemplateParameter(models.Model):
    class Meta:
        verbose_name = _("Code Template Parameter")
        verbose_name_plural = _("Code Template Parameters")

    code_template = models.ForeignKey(  # type: ignore
        CodeTemplate,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="parameters",
        verbose_name=_("Code Template"),
    )

    name = models.CharField(  # type: ignore
        _("name"),
        max_length=60,
        null=False,
        blank=False,
        validators=[MinLengthValidator(MIN_NAME_COMMON_LENGTH)],
        unique=True,
    )

    value = models.CharField(
        _("value"),
        max_length=200,
        null=True,
        blank=True,
    )

    def __str__(self):
        return _("Code Template Parameter: %(ct)s - %(name)s - %(value)s") % {
            "ct": self.code_template.name,
            "name": self.name,
            "value": self.value,
        }


class Project(TimeStampMixin, models.Model):
    def __str__(self) -> str:
        return _("Project: %(user)s - %(project)s") % {
            "user": self.user.username,
            "project": self.name,
        }

    user = models.ForeignKey(  # type: ignore
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("user"),
    )
    name = models.CharField(  # type: ignore
        _("name"),
        max_length=MAX_PROJECT_NAME_LENGTH,
        unique=True,
        null=False,
        blank=False,
        validators=[MinLengthValidator(MIN_PROJECT_NAME_LENGTH)],
    )
    description = models.CharField(  # type: ignore
        _("description"), max_length=1000, null=True, blank=True
    )

    projectsettings = "ProjectSettings"  # forward decl for mypy
    transformationmapping = "TransformationMapping"  # forward decl for mypy

    class Meta:
        ordering = ["name"]
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"pk": self.pk})

    def slug(self):
        return slugify(self.name).replace("-", "_")

    def deploy_filename(self):
        return f"{self.slug()}.zip"


def generate_random_admin_password():
    return uuid4().hex[0:24]


class NullOrMinLengthValidator(BaseValidator):
    message = ngettext_lazy(
        "Ensure this value has at least %(limit_value)d character (it has "
        "%(show_value)d).",
        "Ensure this value has at least %(limit_value)d characters (it has "
        "%(show_value)d).",
        "limit_value",
    )
    code = "min_length"

    def compare(self, a, b):
        return not a or a < b

    def clean(self, x):
        return len(x)


class ProjectSettings(models.Model):
    project = models.OneToOneField(  # type: ignore
        Project,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name=_("project settings"),
    )
    domain_name = models.CharField(  # type: ignore
        _("domain"), max_length=100, null=True, validators=[MinLengthValidator(4)]
    )
    admin_name = models.CharField(  # type: ignore
        _("admin user name"),
        max_length=60,
        # Default admin user name
        default=_("admin"),
        validators=[MinLengthValidator(MIN_USER_NAME_LENGTH)],
    )
    admin_password = models.CharField(  # type: ignore
        _("admin password"),
        max_length=100,
        default=settings.DEFAULT_ADMIN_PASSWORD,
        validators=[MinLengthValidator(MIN_PASSWORD_LENGTH)],
    )
    demo_user_name = models.CharField(  # type: ignore
        _("demo user name"),
        max_length=60,
        null=True,
        blank=True,
        default=_("demo"),
        validators=[NullOrMinLengthValidator(MIN_USER_NAME_LENGTH)],
    )
    demo_user_password = models.CharField(  # type: ignore
        _("demo user password"),
        max_length=100,
        null=True,
        blank=True,
        validators=[NullOrMinLengthValidator(MIN_PASSWORD_LENGTH)],
        help_text=_("Set no password to disable creation of a demo user!"),
    )

    docker_root = models.CharField(  # type: ignore
        _("docker root"),
        max_length=100,
        null=True,
        blank=True,
    )

    code_template = models.ForeignKey(
        CodeTemplate,
        on_delete=models.SET_NULL,
        related_name="projectsettings",
        null=True,
        blank=True,
        verbose_name=_("Code Template"),
    )

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"pk": self.project.id})

    class Meta:
        verbose_name = _("project settings")
        verbose_name_plural = _("project settings")


class TransformationMapping(models.Model):
    project = models.OneToOneField(  # type: ignore
        Project, on_delete=models.CASCADE, primary_key=True, verbose_name=_("project")
    )

    files: models.QuerySet["TransformationFile"]  # forward decl for mypy
    models: models.QuerySet["Model"]  # forward decl for mypy


class TransformationFile(models.Model):
    transformation_mapping = models.ForeignKey(  # type: ignore
        TransformationMapping,
        on_delete=models.CASCADE,
        null=False,
        related_name="files",
        verbose_name=_("transformation mapping"),
    )

    sheets: models.QuerySet["TransformationSheet"]  # forward decl for mypy

    file = models.FileField(
        _("file"),
        max_length=200,
        validators=[FileExtensionValidator(allowed_extensions=VALID_SUFFIXES)],
    )

    class Meta:
        ordering = ["transformation_mapping", "file"]
        unique_together = ["transformation_mapping", "file"]
        verbose_name = _("file")
        verbose_name_plural = _("files")


post_delete.connect(
    file_cleanup,
    sender=TransformationFile,
    dispatch_uid="transformation_file.file_cleanup",
)


class TransformationSheet(models.Model):
    transformation_file = models.ForeignKey(  # type: ignore
        TransformationFile,
        on_delete=models.CASCADE,
        related_name="sheets",
        verbose_name=_("file"),
    )

    headlines: models.QuerySet["TransformationHeadline"]  # forward decl for mypy

    index = models.IntegerField()  # type: ignore
    exclude = models.BooleanField(default=False)  # type: ignore

    class Meta:
        ordering = ["transformation_file", "index"]
        unique_together = ["transformation_file", "index"]


class TransformationHeadline(models.Model):
    transformation_sheet = models.ForeignKey(  # type: ignore
        TransformationSheet,
        on_delete=models.CASCADE,
        related_name="headlines",
        verbose_name=_("sheet"),
    )

    columns: models.QuerySet["TransformationColumn"]  # forward decl for mypy
    model: "Model"  # forward decl for mypy

    row_index = models.IntegerField()  # type: ignore
    exclude = models.BooleanField(default=False)  # type: ignore

    content = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["transformation_sheet", "row_index"]
        unique_together = ["transformation_sheet", "row_index"]


class TransformationColumn(models.Model):
    column_index = models.IntegerField()  # type: ignore
    transformation_headline = models.ForeignKey(  # type: ignore
        TransformationHeadline,
        on_delete=models.CASCADE,
        related_name="columns",
        verbose_name=_("headline"),
    )

    field: "Field"  # forward decl for mypy
    exclude = models.BooleanField(default=False)  # type: ignore

    class Meta:
        ordering = ["transformation_headline", "column_index"]
        unique_together = ["transformation_headline", "column_index"]


class Model(TimeStampMixin, models.Model):
    class Meta:
        ordering = ["index", "transformation_mapping"]
        unique_together = ["index", "transformation_mapping"]
        verbose_name = _("model")
        verbose_name_plural = _("models")

    name = models.CharField(  # type: ignore
        _("name"),
        max_length=100,
        validators=[MinLengthValidator(MIN_MODEL_NAME_LENGTH)],
    )

    description = models.TextField(
        _("description"), max_length=1000, null=True, blank=True  # type: ignore
    )

    transformation_headline = models.OneToOneField(  # type: ignore
        TransformationHeadline,
        on_delete=models.SET_NULL,
        null=True,
        related_name="model",
        verbose_name=_("headline"),
    )
    transformation_mapping = models.ForeignKey(  # type: ignore
        TransformationMapping,
        on_delete=models.CASCADE,
        null=False,
        related_name="models",
        verbose_name=_("transformation mapping"),
    )
    is_main_entity = models.BooleanField(_("main entry"), default=False)  # type: ignore
    index = models.PositiveSmallIntegerField(  # type: ignore
        _("index"), null=True, validators=[MinValueValidator(1)]
    )
    exclude = models.BooleanField(
        _("exclude from creation"), default=False
    )  # type: ignore

    fields: models.QuerySet["Field"]  # forward decl for mypy

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == (
            "index",
            "transformation_mapping",
        ):
            return ngettext_lazy(
                "%(model_name)'s %(field_labels) are not unique.",
                "%(model_name)'s %(field_labels)s are not unique.",
            )
        else:
            return super(Model, self).unique_error_message(model_class, unique_check)

    def __str__(self) -> str:
        return _("Table: %(user)s - %(project)s - %(model)s") % {
            "user": self.transformation_mapping.project.user.username,
            "project": self.transformation_mapping.project.name,
            "model": self.name,
        }


class Field(TimeStampMixin, models.Model):
    class Meta:
        ordering = ["index", "model"]
        unique_together = ["index", "model"]
        verbose_name = _("field")
        verbose_name_plural = _("fields")

    class Datatype(models.IntegerChoices):
        NONE = (
            0,
            _("None"),
        )
        BIG_INTEGER_FIELD = (
            1,
            "BigIntegerField",
        )
        BINARY_FIELD = (
            2,
            "BinaryField",
        )
        BOOLEAN_FIELD = (
            3,
            "BooleanField",
        )
        CHAR_FIELD = (
            4,
            "CharField",
        )
        COMMA_SEPARATED_INTEGER_FIELD = (
            5,
            "CommaSeparatedIntegerField",
        )
        DATE_FIELD = (
            6,
            "DateField",
        )
        DATE_TIME_FIELD = (
            7,
            "DateTimeField",
        )
        DECIMAL_FIELD = (
            8,
            "DecimalField",
        )
        DURATION_FIELD = (
            9,
            "DurationField",
        )
        EMAIL_FIELD = (
            10,
            "EmailField",
        )
        FIELD = (
            11,
            "Field",
        )
        FILE_PATH_FIELD = (
            12,
            "FilePathField",
        )
        FLOAT_FIELD = (
            13,
            "FloatField",
        )
        GENERIC_IPADDRESS_FIELD = (
            14,
            "GenericIPAddressField",
        )
        IPADDRESS_FIELD = (
            15,
            "IPAddressField",
        )
        INTEGER_FIELD = (
            16,
            "IntegerField",
        )
        NULL_BOOLEAN_FIELD = (
            17,
            "NullBooleanField",
        )
        POSITIVE_BIG_INTEGER_FIELD = (
            18,
            "PositiveBigIntegerField",
        )
        POSITIVE_INTEGER_FIELD = (
            19,
            "PositiveIntegerField",
        )
        POSITIVE_SMALL_INTEGER_FIELD = (
            20,
            "PositiveSmallIntegerField",
        )
        SLUG_FIELD = (
            21,
            "SlugField",
        )
        SMALL_AUTO_FIELD = (
            22,
            "SmallAutoField",
        )
        SMALL_INTEGER_FIELD = (
            23,
            "SmallIntegerField",
        )
        TEXT_FIELD = (
            24,
            "TextField",
        )
        TIME_FIELD = (
            25,
            "TimeField",
        )
        URLFIELD = (
            26,
            "URLField",
        )
        UUIDFIELD = (
            27,
            "UUIDField",
        )
        AUTO_FIELD = (
            28,
            "AutoField",
        )
        BIG_AUTO_FIELD = (
            29,
            "BigAutoField",
        )
        FILE_FIELD = (
            30,
            "FileField",
        )
        JSONFIELD = (
            31,
            "JSONField",
        )

        __empty__ = _("(Unknown)")

    DATATYPE_LABEL_BY_VALUE = {k: v for k, v in Datatype.choices}
    CHAR_MAX_LENGTH_STEPS: List[int] = [10, 30, 60, 100, 200, 1000, 2000]

    @staticmethod
    def find_next_step(requested_size: int):
        for step in Field.CHAR_MAX_LENGTH_STEPS:
            if step >= requested_size:
                return step
        return requested_size

    name = models.CharField(  # type: ignore
        _("name"),
        max_length=100,
        validators=[MinLengthValidator(MIN_FIELD_NAME_LENGTH)],
    )

    description = models.TextField(
        _("description"), max_length=1000, null=True, blank=True  # type: ignore
    )

    transformation_column = models.ForeignKey(  # type: ignore
        TransformationColumn,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("transformation column"),
    )
    model = models.ForeignKey(
        Model,
        on_delete=models.CASCADE,
        related_name="fields",
        verbose_name=_("table"),
    )  # type ignore
    datatype = models.IntegerField(  # type: ignore
        _("data type"),
        choices=Datatype.choices,
        default=Datatype.CHAR_FIELD,
    )
    max_length = models.IntegerField(_("field length"), null=True, blank=True)  # type: ignore
    max_digits = models.IntegerField(
        _("decimal number length"), null=True, blank=True
    )  # type:
    # ignore
    decimal_places = models.IntegerField(
        _("decimal places"),
        null=True,
        blank=True,
    )  # type: ignore
    default_value = models.CharField(  # type: ignore
        _("default value"), max_length=100, null=True, blank=True
    )
    choices = models.JSONField(
        _("selection values"), null=True, blank=True
    )  # type: ignore
    blank = models.BooleanField(
        _("allow empty values in form"), default=False
    )  # type: ignore
    null = models.BooleanField(
        _("allow empty values in database"), default=False
    )  # type: ignore
    foreign_key_entity = models.ForeignKey(  # type: ignore
        Model,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("foreign key"),
    )
    is_unique = models.BooleanField(_("unique"), default=False)  # type: ignore
    use_index = models.BooleanField(_("create index"), default=False)  # type: ignore
    validation_pattern = models.CharField(  # type: ignore
        _("validation pattern"), max_length=100, null=True, blank=True
    )
    show_in_list = models.BooleanField(_("show in list page"), default=True)  # type: ignore
    show_in_detail = models.BooleanField(
        _("show in detail page"), default=True
    )  # type:
    # ignore
    exclude = models.BooleanField(_("exclude from creation"), default=False)  # type: ignore
    index = models.PositiveSmallIntegerField(  # type: ignore
        _("index"), null=True, validators=[MinValueValidator(1)]
    )
    internationalizable = models.BooleanField(_("internationalizable"), default=False)  # type: ignore

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == ("index", "model"):
            return "%(model_name)s's %(field_labels)s are not unique."
        else:
            return super(Field, self).unique_error_message(model_class, unique_check)

    def __str__(self) -> str:
        if not hasattr(self, "model"):
            return "-"
        return _("Column: %(user)s - %(project)s - %(model)s - %(column)s") % {
            "user": self.model.transformation_mapping.project.user.username,
            "project": self.model.transformation_mapping.project.name,
            "model": self.model.name,
            "column": self.name,
        }


def validate_file_type(file: TransformationFile) -> None:
    path = Path(file.file.name)
    if path.suffix.replace(".", "") not in VALID_SUFFIXES:
        raise ValidationError(
            ngettext_lazy(
                "Suffix %(suffix) is not allowed for import",
                "Suffix %(suffix) is not allowed for import",
            )
            % {"suffix": path.suffix}
        )
