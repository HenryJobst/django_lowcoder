# Generated by Django 4.1.4 on 2022-12-23 22:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0004_model_project"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="f913e47a33ad4964",
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
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
    ]