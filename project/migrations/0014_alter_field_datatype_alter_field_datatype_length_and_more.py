# Generated by Django 4.1.4 on 2022-12-26 21:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0013_alter_field_datatype_length_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="field",
            name="datatype",
            field=models.CharField(
                default="CharField", max_length=60, verbose_name="Datentyp"
            ),
        ),
        migrations.AlterField(
            model_name="field",
            name="datatype_length",
            field=models.IntegerField(blank=True, null=True, verbose_name="Länge"),
        ),
        migrations.AlterField(
            model_name="field",
            name="default_value",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Standardwert"
            ),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="c9646f43059f4f02b10a473f",
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
    ]
