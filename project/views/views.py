from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_GET
from django.views.generic import ListView
from django_htmx.middleware import HtmxDetails

from project.models import Project


# Typing pattern recommended by django-stubs:
# https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an
# -authenticated-user
class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


# noinspection PyUnusedLocal
@require_GET
def favicon(request: HtmxHttpRequest) -> HttpResponse:
    return HttpResponse(
        (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + '<text y=".9em" font-size="90">&#9889;</text>'
            + "</svg>"
        ),
        content_type="image/svg+xml",
    )


class HttpResponseUnprocessableEntity(HttpResponse):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY


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
            return QuerySet(Project).none()
