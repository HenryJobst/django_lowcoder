from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse

MIN_PASSWORD_LENGTH = 6

MIN_PROJECT_NAME_LENGTH = 4
MAX_PROJECT_NAME_LENGTH = 100

MIN_USER_NAME_LENGTH = 6
MIN_MODEL_NAME_LENGTH = 3
MIN_FIELD_NAME_LENGTH = 2


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Project(TimeStampMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=MAX_PROJECT_NAME_LENGTH,
        unique=True,
        validators=[MinLengthValidator(MIN_PROJECT_NAME_LENGTH)],
    )
    description = models.CharField(max_length=1000)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"pk": self.pk})


class ProjectSettings(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    domain_name = models.CharField(
        max_length=100, null=True, validators=[MinLengthValidator(4)]
    )
    admin_name = models.CharField(
        max_length=60,
        default="admin",
        validators=[MinLengthValidator(MIN_USER_NAME_LENGTH)],
    )
    admin_password = models.CharField(
        max_length=100, validators=[MinLengthValidator(MIN_PASSWORD_LENGTH)]
    )
    demo_user_name = models.CharField(
        max_length=60,
        null=True,
        default="demo",
        validators=[MinLengthValidator(MIN_USER_NAME_LENGTH)],
    )
    demo_user_password = models.CharField(
        max_length=100, null=True, validators=[MinLengthValidator(MIN_PASSWORD_LENGTH)]
    )


class TransformationMapping(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    # files = models.ManyToOneRel('file_id', TransformationFile, )


class TransformationFile(models.Model):
    transformation_mapping = models.ForeignKey(
        TransformationMapping, on_delete=models.CASCADE, null=False
    )
    file_path = models.FilePathField("", unique=True, allow_folders=False)
    file = models.BinaryField()


class TransformationSheet(models.Model):
    transformation_file = models.ForeignKey(
        TransformationFile, on_delete=models.CASCADE
    )
    index = models.IntegerField()


class TransformationHeadline(models.Model):
    transformation_sheet = models.ForeignKey(
        TransformationSheet, on_delete=models.CASCADE
    )
    row_index = models.IntegerField()


class TransformationColumn(models.Model):
    column_index = models.IntegerField()
    transformation_headline = models.ForeignKey(
        TransformationHeadline, on_delete=models.CASCADE
    )


class Model(models.Model):
    name = models.CharField(
        max_length=100, validators=[MinLengthValidator(MIN_MODEL_NAME_LENGTH)]
    )
    transformation_headline = models.ForeignKey(
        TransformationHeadline, on_delete=models.SET_NULL, null=True
    )
    transformation_mapping = models.ForeignKey(
        TransformationMapping, on_delete=models.CASCADE
    )
    is_main_entity = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]


class ModelField(models.Model):
    name = models.CharField(
        max_length=100, validators=[MinLengthValidator(MIN_FIELD_NAME_LENGTH)]
    )
    transformation_column = models.ForeignKey(
        TransformationColumn, on_delete=models.SET_NULL, null=True
    )
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    datatype = models.CharField(max_length=60, default="CharField")
    datatype_length = models.IntegerField(null=True)
    default_value = models.CharField(max_length=100, null=True)
    is_foreign_key = models.BooleanField(default=False)
    foreign_key_entity = models.CharField(max_length=100)
    foreign_key_id = models.CharField(max_length=100)
    is_unique = models.BooleanField(default=False)
    use_index = models.BooleanField(default=False)
    validation_pattern = models.CharField(max_length=100)
    show_in_list = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
