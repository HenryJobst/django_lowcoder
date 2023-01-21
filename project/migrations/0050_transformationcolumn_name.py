# Generated by Django 4.1.5 on 2023-01-21 15:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0049_remove_transformationsheet_content_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="transformationcolumn",
            name="name",
            field=models.CharField(
                default="Default",
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(2)],
                verbose_name="name",
            ),
            preserve_default=False,
        ),
    ]