# Generated by Django 4.1.4 on 2022-12-23 22:43

import django.core.validators
from django.db import migrations, models
import project.models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0005_alter_projectsettings_admin_password_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="0c95dfd906ba408688ef7dfc",
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="demo_user_password",
            field=models.CharField(
                help_text="Kein Passwort setzen, um keinen Demo-User anzulegen!",
                max_length=100,
                null=True,
                validators=[project.models.NullOrMinLengthValidator(6)],
            ),
        ),
    ]