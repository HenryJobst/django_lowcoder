from django.http import HttpRequest

from project.models import Project, Model

SELECTED = "selected"
SELECTED_NAME = "selected_name"

SELECTED_MODEL = "selected_model"
SELECTED_MODEL_NAME = "selected_model_name"


def reset_selection(request: HttpRequest, pk: int) -> bool:
    """
    The reset_selection function is used to reset the selection of a user.
    It takes in an HttpRequest and an integer pk as parameters. It then checks if the selected item is equal to the
    item that was passed in, and if it is, it resets both SELECTED and SELECTED_NAME back to 0 (which means nothing). If
    the items are not equal, then nothing happens.

    :param request:HttpRequest: Get the session
    :param pk:int: Identify the object that is to be selected
    :return: True if the selected item is removed from
    :doc-author: Trelent
    """
    if pk == request.session.get(SELECTED, 0):
        request.session[SELECTED] = 0
        request.session[SELECTED_NAME] = None
        return True
    return False


def reset_model_selection(request: HttpRequest, pk: int) -> bool:
    """
    The reset_model_selection function is used to reset the selected model in the session.
    It takes a request and an integer pk as parameters. It checks if the pk matches with
    the selected model in the session, and if it does, it resets both SELECTED_MODEL and
    SELECTED_MODEL_NAME to 0 (zero) in the session.

    :param request:HttpRequest: Get the session
    :param pk:int: Check if the model is currently selected
    :return: True if the model with id pk is currently selected and sets the
    :doc-author: Trelent
    """
    if pk == request.session.get(SELECTED_MODEL, 0):
        request.session[SELECTED_MODEL] = 0
        request.session[SELECTED_MODEL_NAME] = None
        return True
    return False


def set_selection_name(request: HttpRequest, pk: int) -> None:
    """
    The set_selection_name function is used to set the selected name in the session.
    It takes a request and a pk as arguments, and if that pk matches the selected project
    in the session, it sets that project's name as selected in the session.

    :param request:HttpRequest: Get the current session
    :param pk:int: Get the primary key of the project
    :return: None
    :doc-author: Trelent
    """
    if pk == request.session.get(SELECTED, 0):
        project: Project = Project.objects.get(pk=pk)
        request.session[SELECTED_NAME] = project.name


def set_model_selection_name(request: HttpRequest, pk: int) -> None:
    """
    The set_model_selection_name function is used to set the selected model name in the session.
    It takes a request and a pk as arguments, where pk is the primary key of the model that was clicked on.
    If this pk matches with that stored in SELECTED_MODEL_NAME, then it will do nothing. Otherwise, it will set
    the value of SELECTED_MODEL_NAME to be equal to this new value.

    :param request:HttpRequest: Get the current session
    :param pk:int: Get the model with that primary key
    :return: None
    :doc-author: Trelent
    """
    if pk == request.session.get(SELECTED_MODEL_NAME, 0):
        model: Model = Model.objects.get(pk=pk)
        request.session[SELECTED_MODEL_NAME] = model.name


def set_selection(request: HttpRequest, pk: int) -> None:
    """
    The set_selection function sets the session variable SELECTED to the primary key of a project, and
    sets the session variable SELECTED_NAME to that project's name. This function is called when a user clicks on
    a project in order to select it for further action.

    :param request:HttpRequest: Access the session
    :param pk:int: Identify the project in the database
    :return: None
    :doc-author: Trelent
    """
    request.session[SELECTED] = pk
    request.session[SELECTED_NAME] = Project.objects.get(pk=pk).name


def set_model_selection(request: HttpRequest, pk: int) -> None:
    """
    The set_model_selection function sets the session variable SELECTED_MODEL to the model id passed in as pk.
    It also sets the session variable SELECTED_MODEL_NAME to that model's name.

    :param request:HttpRequest: Get the user's session
    :param pk:int: Get the id of the model that is selected
    :return: None
    :doc-author: Trelent
    """
    request.session[SELECTED_MODEL] = pk
    request.session[SELECTED_MODEL_NAME] = Model.objects.get(pk=pk).name


def toggle_selection(request: HttpRequest, pk: int) -> None:
    """
    The toggle_selection function is used to toggle the selection of a specific
    object in the database. It takes two arguments, request and pk. The request
    argument is an HttpRequest object that contains metadata about the user's
    request (such as which page they're on). The pk argument is an integer that
    represents a specific object in the database. If this object has already been
    selected by this user, then it will be unselected; if it has not been selected
    by this user, then it will be selected.

    :param request:HttpRequest: Get the current session
    :param pk:int: Specify the primary key of the object that is to be selected
    :return: Nothing
    :doc-author: Trelent
    """
    if not reset_selection(request, pk):
        set_selection(request, pk)


def toggle_model_selection(request: HttpRequest, pk: int) -> None:
    """
    The toggle_model_selection function is used to toggle the model selection of a given
    model. If the model is not selected, it will be selected and vice versa. The function
    takes in an HttpRequest object and an integer representing the primary key of a given
    model as parameters. It then checks if there are any models currently selected by the user,
    and if so, it removes all models from that list before adding this one to that list.

    :param request:HttpRequest: Get the user's session
    :param pk:int: Identify the model
    :return: None
    :doc-author: Trelent
    """
    if not reset_model_selection(request, pk):
        set_model_selection(request, pk)
