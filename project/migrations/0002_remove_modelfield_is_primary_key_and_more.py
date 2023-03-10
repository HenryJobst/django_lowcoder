# Generated by Django 4.1.4 on 2022-12-20 10:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="modelfield",
            name="is_primary_key",
        ),
        migrations.AddField(
            model_name="modelfield",
            name="show_in_list",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="projectsettings",
            name="domain_name",
            field=models.CharField(
                max_length=100,
                null=True,
                validators=[django.core.validators.MinLengthValidator(4)],
            ),
        ),
        migrations.AlterField(
            model_name="model",
            name="name",
            field=models.CharField(
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(3)],
            ),
        ),
        migrations.AlterField(
            model_name="modelfield",
            name="name",
            field=models.CharField(
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(2)],
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="name",
            field=models.CharField(
                max_length=100,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(4)],
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_name",
            field=models.CharField(
                default="admin",
                max_length=60,
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="demo_user_name",
            field=models.CharField(
                default="demo",
                max_length=60,
                null=True,
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="demo_user_password",
            field=models.CharField(
                max_length=100,
                null=True,
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
    ]
