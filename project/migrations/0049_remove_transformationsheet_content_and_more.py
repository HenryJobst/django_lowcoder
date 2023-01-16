# Generated by Django 4.1.5 on 2023-01-16 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0048_transformationsheet_content"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transformationsheet",
            name="content",
        ),
        migrations.AddField(
            model_name="transformationheadline",
            name="content",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
