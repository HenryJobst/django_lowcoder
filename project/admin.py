from django.contrib import admin
from project.models import Project, ProjectSettings

# Register your models here.
admin.site.register(Project)
admin.site.register(ProjectSettings)
