# Generated by Django 4.1.4 on 2022-12-28 20:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0022_alter_projectsettings_admin_password_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="8c5c66638c814741a443cf21",
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(6)],
                verbose_name="Administrator-Passwort",
            ),
        ),
        migrations.AlterField(
            model_name="transformationfile",
            name="file",
            field=models.FileField(
                max_length=200,
                unique=True,
                upload_to="",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["csv", "odf", "xls", "xlsx"]
                    )
                ],
                verbose_name="Datei",
            ),
        ),
    ]
