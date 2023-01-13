from django.contrib import admin

from django_lowcoder.admin import admin_site
from project.models import *


class ProjectAdmin(admin.ModelAdmin):
    pass


class ProjectSettingsAdmin(admin.ModelAdmin):
    pass


class ModelAdmin(admin.ModelAdmin):
    pass


class FieldAdmin(admin.ModelAdmin):
    pass


class ProgrammingLanguageAdmin(admin.ModelAdmin):
    pass


class CodeTemplateAdmin(admin.ModelAdmin):
    pass


class CodeTemplateParameterAdmin(admin.ModelAdmin):
    pass


admin_site.register(Project, ProjectAdmin)
admin_site.register(ProjectSettings, ProjectSettingsAdmin)
admin_site.register(Model, ModelAdmin)
admin_site.register(Field, FieldAdmin)
admin_site.register(ProgrammingLanguage, ProgrammingLanguageAdmin)
admin_site.register(CodeTemplate, CodeTemplateAdmin)
admin_site.register(CodeTemplateParameter, CodeTemplateParameterAdmin)
