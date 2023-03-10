# Generated by Django 4.1.4 on 2022-12-27 23:20

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0017_field_created_at_field_updated_at_model_created_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transformationfile",
            name="file_path",
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="ab3294c0fc47446c868f67e5",
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(6)],
                verbose_name="Administrator-Passwort",
            ),
        ),
        migrations.AlterField(
            model_name="transformationfile",
            name="file",
            field=models.FileField(
                max_length=200, unique=True, upload_to="", verbose_name="Datei"
            ),
        ),
        migrations.AlterField(
            model_name="transformationfile",
            name="transformation_mapping",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="files",
                to="project.transformationmapping",
            ),
        ),
    ]
