# Generated by Django 4.1.4 on 2022-12-26 21:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0012_remove_field_foreign_key_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="field",
            name="datatype_length",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="field",
            name="default_value",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="field",
            name="foreign_key_entity",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="Fremdschlüssel-Tabelle",
            ),
        ),
        migrations.AlterField(
            model_name="field",
            name="is_foreign_key",
            field=models.BooleanField(default=False, verbose_name="Fremdschlüssel?"),
        ),
        migrations.AlterField(
            model_name="field",
            name="is_unique",
            field=models.BooleanField(default=False, verbose_name="Eindeutig?"),
        ),
        migrations.AlterField(
            model_name="field",
            name="show_in_list",
            field=models.BooleanField(default=True, verbose_name="Anzeigen?"),
        ),
        migrations.AlterField(
            model_name="field",
            name="use_index",
            field=models.BooleanField(default=False, verbose_name="Index?"),
        ),
        migrations.AlterField(
            model_name="field",
            name="validation_pattern",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="projectsettings",
            name="admin_password",
            field=models.CharField(
                default="f7bde83f0d484cbd86560aa2",
                max_length=100,
                validators=[django.core.validators.MinLengthValidator(6)],
            ),
        ),
    ]
