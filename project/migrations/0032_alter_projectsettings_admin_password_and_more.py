# Generated by Django 4.1.4 on 2023-01-02 21:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0031_alter_model_transformation_headline_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="87b484a4e73645bd998d9c2b",
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