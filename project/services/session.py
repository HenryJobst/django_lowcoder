from django.http import HttpRequest

from project.models import Project, Model

SELECTED = "selected"
SELECTED_NAME = "selected_name"

SELECTED_MODEL = "selected_model"
SELECTED_MODEL_NAME = "selected_model_name"


def reset_selection(request: HttpRequest, pk: int) -> bool:
    if pk == request.session.get(SELECTED, 0):
        request.session[SELECTED] = 0
        request.session[SELECTED_NAME] = None
        return True
    return False


def reset_model_selection(request: HttpRequest, pk: int) -> bool:
    if pk == request.session.get(SELECTED_MODEL, 0):
        request.session[SELECTED_MODEL] = 0
        request.session[SELECTED_MODEL_NAME] = None
        return True
    return False


def set_selection_name(request: HttpRequest, pk: int) -> None:
    if pk == request.session.get(SELECTED, 0):
        project: Project = Project.objects.get(pk=pk)
        request.session[SELECTED_NAME] = project.name


def set_model_selection_name(request: HttpRequest, pk: int) -> None:
    if pk == request.session.get(SELECTED_MODEL_NAME, 0):
        model: Model = Model.objects.get(pk=pk)
        request.session[SELECTED_MODEL_NAME] = model.name


def set_selection(request: HttpRequest, pk: int) -> None:
    request.session[SELECTED] = pk
    request.session[SELECTED_NAME] = Project.objects.get(pk=pk).name


def set_model_selection(request: HttpRequest, pk: int) -> None:
    request.session[SELECTED_MODEL] = pk
    request.session[SELECTED_MODEL_NAME] = Model.objects.get(pk=pk).name


def toggle_selection(request: HttpRequest, pk: int) -> None:
    if not reset_selection(request, pk):
        set_selection(request, pk)


def toggle_model_selection(request: HttpRequest, pk: int) -> None:
    if not reset_model_selection(request, pk):
        set_model_selection(request, pk)
