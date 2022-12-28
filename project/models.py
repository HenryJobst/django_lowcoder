from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinLengthValidator,
    MinValueValidator,
    BaseValidator,
    FileExtensionValidator,
)
from django.db import models
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


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Project(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    name = models.CharField(
        "Name",
        max_length=MAX_PROJECT_NAME_LENGTH,
        unique=True,
        null=False,
        blank=False,
        validators=[MinLengthValidator(MIN_PROJECT_NAME_LENGTH)],
    )
    description = models.CharField(
        "Beschreibung", max_length=1000, null=True, blank=True
    )

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
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    domain_name = models.CharField(
        "Domain", max_length=100, null=True, validators=[MinLengthValidator(4)]
    )
    admin_name = models.CharField(
        "Administrator-Benutzername",
        max_length=60,
        default="admin",
        validators=[MinLengthValidator(MIN_USER_NAME_LENGTH)],
    )
    admin_password = models.CharField(
        "Administrator-Passwort",
        max_length=100,
        default=generate_random_admin_password(),
        validators=[MinLengthValidator(MIN_PASSWORD_LENGTH)],
    )
    demo_user_name = models.CharField(
        "Demo-Nutzer-Benutzername",
        max_length=60,
        null=True,
        blank=True,
        default="demo",
        validators=[NullOrMinLengthValidator(MIN_USER_NAME_LENGTH)],
    )
    demo_user_password = models.CharField(
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
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class TransformationFile(models.Model):
    transformation_mapping = models.ForeignKey(
        TransformationMapping,
        on_delete=models.CASCADE,
        null=False,
        related_name="files",
    )
    file = models.FileField(
        "Datei",
        unique=True,
        max_length=200,
        validators=[FileExtensionValidator(allowed_extensions=VALID_SUFFIXES)],
    )


class TransformationSheet(models.Model):
    transformation_file = models.ForeignKey(
        TransformationFile, on_delete=models.CASCADE, related_name="sheets"
    )
    index = models.IntegerField()


class TransformationHeadline(models.Model):
    transformation_sheet = models.ForeignKey(
        TransformationSheet, on_delete=models.CASCADE, related_name="headlines"
    )
    row_index = models.IntegerField()


class TransformationColumn(models.Model):
    column_index = models.IntegerField()
    transformation_headline = models.ForeignKey(
        TransformationHeadline, on_delete=models.CASCADE, related_name="columns"
    )


class Model(TimeStampMixin, models.Model):
    name = models.CharField(
        "Name", max_length=100, validators=[MinLengthValidator(MIN_MODEL_NAME_LENGTH)]
    )
    transformation_headline = models.OneToOneField(
        TransformationHeadline, on_delete=models.SET_NULL, null=True
    )
    transformation_mapping = models.ForeignKey(
        TransformationMapping,
        on_delete=models.CASCADE,
        null=False,
        related_name="models",
    )
    is_main_entity = models.BooleanField("Haupt-Tabelle?", default=False)
    index = models.PositiveSmallIntegerField(
        "Reihenfolge", null=True, validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ["index"]
        unique_together = ["index", "transformation_mapping"]

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == (
            "index",
            "transformation_mapping",
        ):
            return "%(model_name)s's %(field_labels)s are not unique."
        else:
            return super(Model, self).unique_error_message(model_class, unique_check)


class Field(TimeStampMixin, models.Model):
    DATATYPES = [
        (0, "Keiner"),
        (1, "BigIntegerField"),
        (2, "BinaryField"),
        (3, "BooleanField"),
        (4, "CharField"),
        (5, "CommaSeparatedIntegerField"),
        (6, "DateField"),
        (7, "DateTimeField"),
        (8, "DecimalField"),
        (9, "DurationField"),
        (10, "EmailField"),
        (11, "Field"),
        (12, "FilePathField"),
        (13, "FloatField"),
        (14, "GenericIPAddressField"),
        (15, "IPAddressField"),
        (16, "IntegerField"),
        (17, "NullBooleanField"),
        (18, "PositiveBigIntegerField"),
        (19, "PositiveIntegerField"),
        (20, "PositiveSmallIntegerField"),
        (21, "SlugField"),
        (22, "SmallAutoField"),
        (23, "SmallIntegerField"),
        (24, "TextField"),
        (25, "TimeField"),
        (26, "URLField"),
        (27, "UUIDField"),
    ]

    name = models.CharField(
        "Name", max_length=100, validators=[MinLengthValidator(MIN_FIELD_NAME_LENGTH)]
    )
    transformation_column = models.ForeignKey(
        TransformationColumn, on_delete=models.SET_NULL, null=True
    )
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="fields")
    datatype = models.IntegerField(
        "Datentyp", choices=DATATYPES, default=DATATYPES[4][0]
    )
    datatype_length = models.IntegerField("Länge", null=True, blank=True)
    default_value = models.CharField(
        "Standardwert", max_length=100, null=True, blank=True
    )
    foreign_key_entity = models.ForeignKey(
        Model, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_unique = models.BooleanField("Eindeutig?", default=False, blank=True)
    use_index = models.BooleanField("Index?", default=False)
    validation_pattern = models.CharField(
        "Prüfmuster", max_length=100, null=True, blank=True
    )
    show_in_list = models.BooleanField("Anzeigen?", default=True)
    index = models.PositiveSmallIntegerField(
        "Reihenfolge", null=True, validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ["index"]
        unique_together = ["index", "model"]

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == ("index", "model"):
            return "%(model_name)s's %(field_labels)s are not unique."
        else:
            return super(Field, self).unique_error_message(model_class, unique_check)


def validate_file_type(file: TransformationFile) -> None:
    path = Path(file.file.name)
    if path.suffix.replace(".", "") not in VALID_SUFFIXES:
        raise ValidationError(
            f"Der Dateityp {path.suffix} ist ein unzulässiger Dateityp für den Import"
        )
