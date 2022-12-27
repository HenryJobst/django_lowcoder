from django import template
from django.utils.safestring import mark_safe

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
