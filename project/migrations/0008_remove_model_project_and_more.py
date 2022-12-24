# Generated by Django 4.1.4 on 2022-12-24 00:04

import django.core.validators
from django.db import migrations, models
import project.models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0007_alter_projectsettings_admin_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="model",
            name="project",
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="1ba369c86dd649c39a63774d",
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="demo_user_password",
            field=models.CharField(
                default="59fc92868a2f47fd8d315910",
                help_text="Kein Passwort setzen, um keinen Demo-User anzulegen!",
                max_length=100,
                null=True,
                validators=[project.models.NullOrMinLengthValidator(6)],
            ),
        ),
    ]
