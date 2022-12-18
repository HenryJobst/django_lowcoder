from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from project.models import Project


@method_decorator(login_required, name='dispatch')
class IndexView(ListView):
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
            return QuerySet()
