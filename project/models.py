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
from django.utils.translation import ngettext_lazy

MIN_PASSWORD_LENGTH = 6

MIN_PROJECT_NAME_LENGTH = 4
MAX_PROJECT_NAME_LENGTH = 100

MIN_USER_NAME_LENGTH = 4
MIN_MODEL_NAME_LENGTH = 3
MIN_FIELD_NAME_LENGTH = 2

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
    created_at = models.DateTimeField(auto_now_add=True)  # type: ignore
    updated_at = models.DateTimeField(auto_now=True)  # type: ignore

    class Meta:
        abstract = True


class Project(TimeStampMixin, models.Model):
    def __str__(self) -> str:
        return f"Projekt: {self.name} - User: {self.user.username}"

    user = models.ForeignKey(  # type: ignore
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    name = models.CharField(  # type: ignore
        "Name",
        max_length=MAX_PROJECT_NAME_LENGTH,
        unique=True,
        null=False,
        blank=False,
        validators=[MinLengthValidator(MIN_PROJECT_NAME_LENGTH)],
    )
    description = models.CharField(  # type: ignore
        "Beschreibung", max_length=1000, null=True, blank=True
    )

    projectsettings = "ProjectSettings"  # forward decl for mypy

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"pk": self.pk})


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
    )
    domain_name = models.CharField(  # type: ignore
        "Domain", max_length=100, null=True, validators=[MinLengthValidator(4)]
    )
    admin_name = models.CharField(  # type: ignore
        "Administrator-Benutzername",
        max_length=60,
        default="admin",
        validators=[MinLengthValidator(MIN_USER_NAME_LENGTH)],
    )
    admin_password = models.CharField(  # type: ignore
        "Administrator-Passwort",
        max_length=100,
        default=settings.DEFAULT_ADMIN_PASSWORD,
        validators=[MinLengthValidator(MIN_PASSWORD_LENGTH)],
    )
    demo_user_name = models.CharField(  # type: ignore
        "Demo-Nutzer-Benutzername",
        max_length=60,
        null=True,
        blank=True,
        default="demo",
        validators=[NullOrMinLengthValidator(MIN_USER_NAME_LENGTH)],
    )
    demo_user_password = models.CharField(  # type: ignore
        "Demo-Nutzer-Passwort",
        max_length=100,
        null=True,
        blank=True,
        validators=[NullOrMinLengthValidator(MIN_PASSWORD_LENGTH)],
        help_text="Kein Passwort setzen, um keinen Demo-User anzulegen!",
    )

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"pk": self.project.id})


class TransformationMapping(models.Model):
    project = models.OneToOneField(  # type: ignore
        Project,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    files: models.QuerySet["TransformationFile"]  # forward decl for mypy
    models: models.QuerySet["Model"]  # forward decl for mypy


class TransformationFile(models.Model):
    transformation_mapping = models.ForeignKey(  # type: ignore
        TransformationMapping,
        on_delete=models.CASCADE,
        null=False,
        related_name="files",
    )

    sheets: models.QuerySet["TransformationSheet"]  # forward decl for mypy

    file = models.FileField(
        "Datei",
        max_length=200,
        validators=[FileExtensionValidator(allowed_extensions=VALID_SUFFIXES)],
    )

    class Meta:
        ordering = ["transformation_mapping", "file"]
        unique_together = ["transformation_mapping", "file"]


post_delete.connect(
    file_cleanup,
    sender=TransformationFile,
    dispatch_uid="transformation_file.file_cleanup",
)


class TransformationSheet(models.Model):
    transformation_file = models.ForeignKey(  # type: ignore
        TransformationFile, on_delete=models.CASCADE, related_name="sheets"
    )

    headlines: models.QuerySet["TransformationHeadline"]  # forward decl for mypy

    index = models.IntegerField()  # type: ignore
    exclude = models.BooleanField(default=False)  # type: ignore

    class Meta:
        ordering = ["transformation_file", "index"]
        unique_together = ["transformation_file", "index"]


class TransformationHeadline(models.Model):
    transformation_sheet = models.ForeignKey(  # type: ignore
        TransformationSheet, on_delete=models.CASCADE, related_name="headlines"
    )

    columns: models.QuerySet["TransformationColumn"]  # forward decl for mypy
    model: "Model"  # forward decl for mypy

    row_index = models.IntegerField()  # type: ignore
    exclude = models.BooleanField(default=False)  # type: ignore

    class Meta:
        ordering = ["transformation_sheet", "row_index"]
        unique_together = ["transformation_sheet", "row_index"]


class TransformationColumn(models.Model):
    column_index = models.IntegerField()  # type: ignore
    transformation_headline = models.ForeignKey(  # type: ignore
        TransformationHeadline, on_delete=models.CASCADE, related_name="columns"
    )

    field: "Field"  # forward decl for mypy
    exclude = models.BooleanField(default=False)  # type: ignore

    class Meta:
        ordering = ["transformation_headline", "column_index"]
        unique_together = ["transformation_headline", "column_index"]


class Model(TimeStampMixin, models.Model):

    name = models.CharField(  # type: ignore
        "Name", max_length=100, validators=[MinLengthValidator(MIN_MODEL_NAME_LENGTH)]
    )

    description = models.TextField(
        "Beschreibung", max_length=1000, null=True, blank=True  # type: ignore
    )

    transformation_headline = models.OneToOneField(  # type: ignore
        TransformationHeadline,
        on_delete=models.SET_NULL,
        null=True,
        related_name="model",
    )
    transformation_mapping = models.ForeignKey(  # type: ignore
        TransformationMapping,
        on_delete=models.CASCADE,
        null=False,
        related_name="models",
    )
    is_main_entity = models.BooleanField("Haupt-Tabelle?", default=False)  # type: ignore
    index = models.PositiveSmallIntegerField(  # type: ignore
        "Reihenfolge", null=True, validators=[MinValueValidator(1)]
    )
    exclude = models.BooleanField("nicht anlegen", default=False)  # type: ignore

    fields: models.QuerySet["Field"]  # forward decl for mypy

    class Meta:
        ordering = ["index", "transformation_mapping"]
        unique_together = ["index", "transformation_mapping"]

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == (
            "index",
            "transformation_mapping",
        ):
            return "%(model_name)s's %(field_labels)s are not unique."
        else:
            return super(Model, self).unique_error_message(model_class, unique_check)

    def __str__(self) -> str:
        return f"Tabelle: {self.name}"


class Field(TimeStampMixin, models.Model):
    DATATYPES = [
        "Keiner",
        "BigIntegerField",
        "BinaryField",
        "BooleanField",
        "CharField",
        "CommaSeparatedIntegerField",
        "DateField",
        "DateTimeField",
        "DecimalField",
        "DurationField",
        "EmailField",
        "Field",
        "FilePathField",
        "FloatField",
        "GenericIPAddressField",
        "IPAddressField",
        "IntegerField",
        "NullBooleanField",
        "PositiveBigIntegerField",
        "PositiveIntegerField",
        "PositiveSmallIntegerField",
        "SlugField",
        "SmallAutoField",
        "SmallIntegerField",
        "TextField",
        "TimeField",
        "URLField",
        "UUIDField",
        "AutoField",
        "BigAutoField",
        "FileField",
        "JSONField",
    ]
    DATATYPE_CHOICES = [(k, v) for k, v in enumerate(DATATYPES)]
    DATATYPE_ID_BY_DATATYPE = {v: k for k, v in enumerate(DATATYPES)}

    CHAR_MAX_LENGTH_STEPS: List[int] = [10, 30, 60, 100, 200, 1000, 2000]

    @staticmethod
    def find_next_step(requested_size: int):
        for step in Field.CHAR_MAX_LENGTH_STEPS:
            if step >= requested_size:
                return step
        return requested_size

    name = models.CharField(  # type: ignore
        "Name", max_length=100, validators=[MinLengthValidator(MIN_FIELD_NAME_LENGTH)]
    )

    description = models.TextField(
        "Beschreibung", max_length=1000, null=True, blank=True  # type: ignore
    )

    transformation_column = models.ForeignKey(  # type: ignore
        TransformationColumn, on_delete=models.SET_NULL, null=True
    )
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="fields")  # type: ignore
    datatype = models.IntegerField(  # type: ignore
        "Datentyp", choices=DATATYPE_CHOICES, default=DATATYPES[4][0]
    )
    max_length = models.IntegerField("Länge", null=True, blank=True)  # type: ignore
    max_digits = models.IntegerField("Anzahl der Stellen bei einer Dezimalzahl", null=True, blank=True)  # type: ignore
    decimal_places = models.IntegerField(
        "Anzahl der Nachkommastellen bei einer Dezimalzahl", null=True, blank=True
    )  # type: ignore
    default_value = models.CharField(  # type: ignore
        "Standardwert", max_length=100, null=True, blank=True
    )
    choices = models.JSONField("Auswahlwerte", null=True, blank=True)  # type: ignore
    blank = models.BooleanField("leeres Eingabefeld zulässig?", default=False)  # type: ignore
    null = models.BooleanField("leerer Spaltenwert zulässig?", default=False)  # type: ignore
    foreign_key_entity = models.ForeignKey(  # type: ignore
        Model,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Fremdschlüssel",
    )
    is_unique = models.BooleanField("Eindeutig?", default=False)  # type: ignore
    use_index = models.BooleanField("Index?", default=False)  # type: ignore
    validation_pattern = models.CharField(  # type: ignore
        "Prüfmuster", max_length=100, null=True, blank=True
    )
    show_in_list = models.BooleanField("in Liste anzeigen?", default=True)  # type: ignore
    show_in_detail = models.BooleanField("in Detailansicht anzeigen?", default=True)  # type: ignore
    exclude = models.BooleanField("nicht anlegen", default=False)  # type: ignore
    index = models.PositiveSmallIntegerField(  # type: ignore
        "Reihenfolge", null=True, validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ["index", "model"]
        unique_together = ["index", "model"]

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == ("index", "model"):
            return "%(model_name)s's %(field_labels)s are not unique."
        else:
            return super(Field, self).unique_error_message(model_class, unique_check)

    def __str__(self) -> str:
        return f"Spalte: {self.name}"


def validate_file_type(file: TransformationFile) -> None:
    path = Path(file.file.name)
    if path.suffix.replace(".", "") not in VALID_SUFFIXES:
        raise ValidationError(
            f"Der Dateityp {path.suffix} ist ein unzulässiger Dateityp für den Import"
        )


class ProgrammingLanguage(models.Model):
    name = models.CharField(  # type: ignore
        "Programmiersprache",
        max_length=60,
        null=False,
        blank=False,
        validators=[MinLengthValidator(1)],
        unique=True,
    )

    def __str__(self):
        return f"Programmiersprache: {self.name}"


class CodeTemplate(models.Model):
    path = models.CharField(  # type: ignore
        "URL/Pfad",
        max_length=200,
        null=False,
        blank=False,
        validators=[MinLengthValidator(1)],
        unique=True,
    )
    programming_language = models.ForeignKey(  # type: ignore
        ProgrammingLanguage, null=False, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Code-Template: {self.programming_language.name} - {self.path}"
