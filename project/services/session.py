from project.models import Project

SELECTED = 'selected'
SELECTED_NAME = 'selected_name'


def reset_selection(request, pk: int) -> bool:
    if pk == request.session.get(SELECTED, 0):
        request.session[SELECTED] = 0
        request.session[SELECTED_NAME] = None
        return True
    return False


def set_selection_name(request, pk: int) -> None:
    if pk == request.session.get(SELECTED, 0):
        project: Project = Project.objects.get(pk=pk)
        request.session[SELECTED_NAME] = project.name


def set_selection(request, pk: int) -> None:
    request.session[SELECTED] = pk
    request.session[SELECTED_NAME] = Project.objects.get(pk=pk).name


def toggle_selection(request, pk: int) -> None:
    if not reset_selection(request, pk):
        set_selection(request, pk)
