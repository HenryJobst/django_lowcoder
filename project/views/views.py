from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic import ListView

from project.models import Project


class IndexView(LoginRequiredMixin, ListView):
    model = Project
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            if user.is_superuser:
                return Project.objects.all()
            else:
                return Project.objects.filter(user=user)
        else:
            return QuerySet(Project)
