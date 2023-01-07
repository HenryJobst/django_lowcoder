# Generated by Django 4.1.5 on 2023-01-07 11:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0039_alter_field_options_alter_model_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="codetemplate",
            name="name",
            field=models.CharField(
                max_length=60,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(4)],
                verbose_name="name",
            ),
        ),
    ]
