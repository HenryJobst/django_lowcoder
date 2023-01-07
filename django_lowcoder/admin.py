from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _


class DlcAdminSite(admin.AdminSite):
    site_header = _("Django LowCoder - Administration")  # type: ignore


admin_site = DlcAdminSite(name="dlc-admin")
admin_site.register(User)
admin_site.register(Group)
