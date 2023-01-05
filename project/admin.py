from django.contrib import admin

from project.models import (
    Project,
    ProjectSettings,
    Model,
    Field,
    ProgrammingLanguage,
    CodeTemplate,
)

admin.site.register(Project)
admin.site.register(ProjectSettings)
admin.site.register(Model)
admin.site.register(Field)
admin.site.register(ProgrammingLanguage)
admin.site.register(CodeTemplate)
