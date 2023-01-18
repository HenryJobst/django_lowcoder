from django.db.models import IntegerChoices

from django.utils.translation import gettext_lazy as _


class Deploytype(IntegerChoices):
    LOCAL = (
        0,
        _("Local Directory"),
    )
    GIT = (
        1,
        _("Git Repository"),
    )
    DOCKER = (
        2,
        _("Docker/Docker-Compose"),
    )
    PAAS = (
        3,
        _("PaaS"),
    )
