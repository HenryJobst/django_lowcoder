from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, \
    DeleteView, \
    UpdateView, \
    FormView

from project.forms.forms_project import ProjectEditForm, ProjectDeleteForm, \
    ProjectDeployForm
from project.models import Project


@method_decorator(login_required, name='dispatch')
class ProjectDetailView(DetailView):
    model = Project


@method_decorator(login_required, name='dispatch')
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectEditForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectEditForm

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        context[
            'next_url'] = self.request.GET.get('next')  # pass `next`
        # parameter received from previous page to the context
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('index')


@method_decorator(login_required, name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    form_class = ProjectDeleteForm
    success_url = reverse_lazy('index')


@method_decorator(login_required, name='dispatch')
class ProjectDeployView(FormView):
    template_name = 'project_deploy.html'
    form_class = ProjectDeployForm
    success_url = '/thanks/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super().form_valid(form)
    pass
