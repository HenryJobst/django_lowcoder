# Generated by Django 4.1.4 on 2022-12-27 13:44

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import project.models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0016_alter_field_is_unique_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="field",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="field",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="model",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="model",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="field",
            name="index",
            field=models.PositiveSmallIntegerField(
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Reihenfolge",
            ),
        ),
        migrations.AlterField(
            model_name="field",
            name="name",
            field=models.CharField(
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(2)],
                verbose_name="Name",
            ),
        ),
        migrations.AlterField(
            model_name="field",
            name="validation_pattern",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Prüfmuster"
            ),
        ),
        migrations.AlterField(
            model_name="model",
            name="index",
            field=models.PositiveSmallIntegerField(
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Reihenfolge",
            ),
        ),
        migrations.AlterField(
            model_name="model",
            name="name",
            field=models.CharField(
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(3)],
                verbose_name="Name",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="description",
            field=models.CharField(
                blank=True, max_length=1000, null=True, verbose_name="Beschreibung"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="name",
            field=models.CharField(
                max_length=100,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(4)],
                verbose_name="Name",
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_name",
            field=models.CharField(
                default="admin",
                max_length=60,
                validators=[django.core.validators.MinLengthValidator(4)],
                verbose_name="Administrator-Benutzername",
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="5ea50254f28f4770b75743e0",
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(6)],
                verbose_name="Administrator-Passwort",
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="demo_user_name",
            field=models.CharField(
                blank=True,
                default="demo",
                max_length=60,
                null=True,
                validators=[project.models.NullOrMinLengthValidator(4)],
                verbose_name="Demo-Nutzer-Benutzername",
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="demo_user_password",
            field=models.CharField(
                blank=True,
                help_text="Kein Passwort setzen, um keinen Demo-User anzulegen!",
                max_length=100,
                null=True,
                validators=[project.models.NullOrMinLengthValidator(6)],
                verbose_name="Demo-Nutzer-Passwort",
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="domain_name",
            field=models.CharField(
                max_length=100,
                null=True,
                validators=[django.core.validators.MinLengthValidator(4)],
                verbose_name="Domain",
            ),
        ),
    ]
