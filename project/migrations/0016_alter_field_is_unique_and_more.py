# Generated by Django 4.1.4 on 2022-12-26 22:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0015_remove_field_is_foreign_key_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="field",
            name="is_unique",
            field=models.BooleanField(
                blank=True, default=False, verbose_name="Eindeutig?"
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="2682255ef2cf495c8ad39a3c",
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
    ]