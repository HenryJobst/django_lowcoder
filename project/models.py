from django.conf import settings
from django.db import models


class Project(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        null=False
        )
    name = models.CharField(max_length=100, null=False, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=1000)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    # mapping = models.OneToOneRel(field='mapping_id', to=TransformationMapping)


class TransformationMapping(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.RESTRICT,
        null=False
        )
    #files = models.ManyToOneRel('file_id', TransformationFile, )


class TransformationFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    transformation_mapping = models.ForeignKey(
        TransformationMapping,
        on_delete=models.RESTRICT,
        null=False)
    file_path = models.FilePathField('', unique=True,
                                     allow_folders=False, null=False)
    file = models.BinaryField(null=False)


class TransformationSheet(models.Model):
    id = models.BigAutoField(primary_key=True)
    transformation_file = models.ForeignKey(
        TransformationFile,
        on_delete=models.RESTRICT, null=False)
    index = models.IntegerField(null=False)


class TransformationHeadline(models.Model):
    id = models.BigAutoField(primary_key=True)
    transformation_sheet = models.ForeignKey(
        TransformationSheet,
        on_delete=models.RESTRICT,
        null=False)
    row_index = models.IntegerField(null=False)


class TransformationColumn(models.Model):
    id = models.BigAutoField(primary_key=True)
    column_index = models.IntegerField(null=False)
    transformation_headline = models.ForeignKey(
        TransformationHeadline,
        on_delete=models.RESTRICT,
        null=False)


class TransformationEntity(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    transformation_headline = models.ForeignKey(
        TransformationHeadline,
        on_delete=models.RESTRICT)
    transformation_mapping = models.ForeignKey(
        TransformationMapping,
        on_delete=models.RESTRICT,
        null=False)


class TransformationField(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    transformation_column = models.ForeignKey(
        TransformationColumn,
        on_delete=models.RESTRICT)
    entity = models.ForeignKey(TransformationEntity,
                               on_delete=models.RESTRICT, null=False)
    is_primary_key = models.BooleanField(null=False)
    datatype = models.CharField(max_length=60, null=False, default='CharField')
    datatype_length = models.IntegerField(null=True)
    is_foreign_key = models.BooleanField(null=False, default=False)
    foreign_key_entity = models.CharField(max_length=100)
    foreign_key_id = models.CharField(max_length=100)
    is_unique = models.BooleanField(null=False, default=False)
    use_index = models.BooleanField(null=False, default=False)
