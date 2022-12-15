from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User

from project.forms import RegisterForm
from project.models import Project


def index(request):
    session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
    return HttpResponse("Hallo, willkommen beim Django-LowCoder. Dein "
                        "Session-Key ist " + session_key)


class RegisterView(generic.CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'



class IndexView(generic.ListView):
    model = Project
    paginate_by = 5

    # context_object_name = 'items'

    def get_queryset(self):
        user = None
        if self.request.user.is_authenticated:
            user = self.request.user
            return Project.objects.filter(user=user)
        else:
            session_key = self.request.COOKIES.get(settings.SESSION_COOKIE_NAME,
                                               None)
            return Project.objects.filter(session_key=session_key)
