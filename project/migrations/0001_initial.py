# Generated by Django 4.1.4 on 2022-12-18 21:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Model",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("is_main_entity", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.CharField(max_length=1000)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="TransformationFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file_path", models.FilePathField(unique=True, verbose_name="")),
                ("file", models.BinaryField()),
            ],
        ),
        migrations.CreateModel(
            name="ProjectSettings",
            fields=[
                (
                    "project",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="project.project",
                    ),
                ),
                ("admin_name", models.CharField(default="admin", max_length=60)),
                ("admin_password", models.CharField(max_length=100)),
                (
                    "demo_user_name",
                    models.CharField(default="demo", max_length=60, null=True),
                ),
                ("demo_user_password", models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="TransformationMapping",
            fields=[
                (
                    "project",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="project.project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TransformationSheet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("index", models.IntegerField()),
                (
                    "transformation_file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="project.transformationfile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TransformationHeadline",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("row_index", models.IntegerField()),
                (
                    "transformation_sheet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="project.transformationsheet",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TransformationColumn",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("column_index", models.IntegerField()),
                (
                    "transformation_headline",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="project.transformationheadline",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ModelField",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("is_primary_key", models.BooleanField()),
                ("datatype", models.CharField(default="CharField", max_length=60)),
                ("datatype_length", models.IntegerField(null=True)),
                ("default_value", models.CharField(max_length=100, null=True)),
                ("is_foreign_key", models.BooleanField(default=False)),
                ("foreign_key_entity", models.CharField(max_length=100)),
                ("foreign_key_id", models.CharField(max_length=100)),
                ("is_unique", models.BooleanField(default=False)),
                ("use_index", models.BooleanField(default=False)),
                ("validation_pattern", models.CharField(max_length=100)),
                (
                    "model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="project.model"
                    ),
                ),
                (
                    "transformation_column",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="project.transformationcolumn",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="model",
            name="transformation_headline",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="project.transformationheadline",
            ),
        ),
        migrations.AddField(
            model_name="transformationfile",
            name="transformation_mapping",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="project.transformationmapping",
            ),
        ),
        migrations.AddField(
            model_name="model",
            name="transformation_mapping",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="project.transformationmapping",
            ),
        ),
    ]
