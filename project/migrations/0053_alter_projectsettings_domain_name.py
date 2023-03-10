# Generated by Django 4.1.5 on 2023-01-24 09:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0052_transformationmapping_deployed_archive_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectsettings",
            name="domain_name",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                validators=[django.core.validators.MinLengthValidator(4)],
                verbose_name="domain",
            ),
        ),
    ]
