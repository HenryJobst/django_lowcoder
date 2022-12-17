from django.conf import settings
from django.db import models


class Project(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=1000)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    # mapping = models.OneToOneRel(field='mapping_id', to=TransformationMapping)


class ProjectSettings(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False
        )
    admin_name = models.CharField(max_length=60, null=False, default='admin')
    admin_password = models.CharField(max_length=100, null=False)
    demo_user_name = models.CharField(max_length=60, null=True, default='demo')
    demo_user_password = models.CharField(max_length=100, null=True)


class TransformationMapping(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False
        )
    # files = models.ManyToOneRel('file_id', TransformationFile, )


class TransformationFile(models.Model):
    transformation_mapping = models.ForeignKey(
        TransformationMapping,
        on_delete=models.CASCADE,
        null=False)
    file_path = models.FilePathField('', unique=True,
                                     allow_folders=False, null=False)
    file = models.BinaryField(null=False)


class TransformationSheet(models.Model):
    transformation_file = models.ForeignKey(
        TransformationFile,
        on_delete=models.CASCADE, null=False)
    index = models.IntegerField(null=False)


class TransformationHeadline(models.Model):
    transformation_sheet = models.ForeignKey(
        TransformationSheet,
        on_delete=models.CASCADE,
        null=False)
    row_index = models.IntegerField(null=False)


class TransformationColumn(models.Model):
    column_index = models.IntegerField(null=False)
    transformation_headline = models.ForeignKey(
        TransformationHeadline,
        on_delete=models.CASCADE,
        null=False)


class Model(models.Model):
    name = models.CharField(max_length=100, null=False)
    transformation_headline = models.ForeignKey(
        TransformationHeadline,
        on_delete=models.SET_NULL, null=True)
    transformation_mapping = models.ForeignKey(
        TransformationMapping,
        on_delete=models.CASCADE,
        null=False)
    is_main_entity = models.BooleanField(null=False, default=False)


class ModelField(models.Model):
    name = models.CharField(max_length=100, null=False)
    transformation_column = models.ForeignKey(
        TransformationColumn,
        on_delete=models.SET_NULL, null=True)
    model = models.ForeignKey(Model,
                              on_delete=models.CASCADE, null=False)
    is_primary_key = models.BooleanField(null=False)
    datatype = models.CharField(max_length=60, null=False, default='CharField')
    datatype_length = models.IntegerField(null=True)
    default_value = models.CharField(max_length=100, null=True)
    is_foreign_key = models.BooleanField(null=False, default=False)
    foreign_key_entity = models.CharField(max_length=100)
    foreign_key_id = models.CharField(max_length=100)
    is_unique = models.BooleanField(null=False, default=False)
    use_index = models.BooleanField(null=False, default=False)
    validation_pattern = models.CharField(max_length=100)
