from django import template
from django.utils.safestring import mark_safe

from project.models import (
    TransformationFile,
    TransformationHeadline,
    TransformationColumn,
    Project,
    Field,
    Model,
)

register = template.Library()

"""
Idea comes from: https://bradmontgomery.net/blog/django-iconbool-filter/
"""


@register.filter("iconbool", is_safe=True)
def iconbool(value):
    """Given a boolean value, this filter outputs a feather icon + the
    word "Ja" or "Nein"

    Example Usage:

        {{ user.has_widget|iconbool }}

    """
    if bool(value):
        result = (
            '<i class="feather-24" data-feather="check-square" title="Ja" aria-hidden="true"></i>'
            '<span class="visually-hidden">Ja</span>'
        )
    else:
        result = (
            '<i class="feather-24" data-feather="x-square" title="Nein" aria-hidden="true"></i>'
            '<span class="visually-hidden">Nein</span>'
        )

    return mark_safe(result)


@register.filter("sheets_count", is_safe=True)
def sheets_count(file: TransformationFile) -> int:
    if isinstance(file, TransformationFile):
        return file.sheets.count() if file.sheets else 0
    raise TypeError("Call of sheets_count with an invalid type.")


@register.filter("headlines_count", is_safe=True)
def headlines_count(file: TransformationFile) -> int:
    if isinstance(file, TransformationFile):
        return TransformationHeadline.objects.filter(
            transformation_sheet__transformation_file=file
        ).count()
    raise TypeError("Call of headlines_count with an invalid type.")


@register.filter("columns_count", is_safe=True)
def columns_count(file: TransformationFile) -> int:
    if isinstance(file, TransformationFile):
        return TransformationColumn.objects.filter(
            transformation_headline__transformation_sheet__transformation_file=file
        ).count()
    raise TypeError("Call of columns_count with an invalid type.")


@register.filter("models_count", is_safe=True)
def models_count(project: Project) -> int:
    if isinstance(project, Project):
        return Model.objects.filter(transformation_mapping__project=project).count()
    raise TypeError("Call of models_count with an invalid type.")


@register.filter("fields_count", is_safe=True)
def fields_count(project: Project) -> int:
    if isinstance(project, Project):
        return Field.objects.filter(
            model__transformation_mapping__project=project
        ).count()
    raise TypeError("Call of fields_count with an invalid type.")


@register.filter("datatype_as_str", is_safe=True)
def datatype_as_str(datatype) -> str:
    return Field.DATATYPES[datatype]
