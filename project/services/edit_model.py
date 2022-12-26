from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from project.models import Model, TransformationMapping, Project


def set_index(model: Model, index: int) -> None:
    """
    The set_index function is a helper function that allows us to change the index of a model.
    It does this by first checking if there are any other models with the same transformation_mapping and index,
    and if so, it switches their indexes. If not, it simply saves the model with its new index.

    :param model:Model: Specify the model that is being modified
    :param index:int: Indicate which index the model should be saved with
    :return: None
    :doc-author: Trelent
    """
    other_model = Model.objects.filter(
        transformation_mapping=model.transformation_mapping,
        index=index,
    ).first()
    if other_model:
        switch_index(model, other_model)
    else:
        save_with_index(model, index)


def save_with_index(model: Model, index: int) -> int:
    """
    The save_with_index function is a helper function that allows us to save the model with an index.
    It also returns the old index of the model, which can be used to update other models.

    :param model:Model: Save the model
    :param index:int: Specify the index of the model in a list
    :return: The old index of the model
    :doc-author: Trelent
    """
    old_index = model.index
    model.index = index
    model.save()
    return old_index


def switch_index(actual_model: Model, other_model: Model) -> None:
    """
    The switch_index function is used to switch the order of two models in a transformation mapping.
    It does this by temporarily setting other_model.index to max used index + 1 to not violate unique constraint on
    index,
    then saving actual_model with other_model's old index, and finally saving other_model with actual model's old index.

    :param actual_model:Model: Get the actual model that is being switched
    :param other_model:Model: Get the model instance from the database
    :return: None
    :doc-author: Trelent
    """
    # temporarily set other_model.index to max used index + 1 to not violate unique constraint on index
    max_index = get_max_index(actual_model.transformation_mapping)
    other_model_index = save_with_index(other_model, max_index + 1)
    actual_model_index = save_with_index(actual_model, other_model_index)
    save_with_index(other_model, actual_model_index)


def get_max_index(tm: TransformationMapping) -> int:
    """
    The get_max_index function returns the maximum index value of all models
    that are associated with a given transformation mapping.  This is useful for
    ensuring that each model has an index value unique from all other models in the
    transformation mapping.  The get_max_index function accepts one argument, tm, which is a TransformationMapping
    object.

    :param tm:TransformationMapping: Filter the model
    :return: The maximum index of the model objects that have a transformationmapping object with the same id as tm
    :doc-author: Trelent
    """
    return (
        Model.objects.filter(transformation_mapping=tm)
        .aggregate(max=Max("index"))
        .get("max", 0)
    )


def model_up(*args, **kwargs) -> Model:
    """
    The model_up function takes a Model object as an argument and returns the model with index one less than the
    argument's index. If the argument is already at its lowest possible index, it will return that model unchanged.

    :param *args: Pass a variable number of arguments to a function
    :param **kwargs: Pass a keyworded, variable-length argument dictionary to the function
    :return: The model object that is found by the get_object_or_404 function
    :doc-author: Trelent
    """
    actual_model: Model = get_object_or_404(Model, *args, **kwargs)
    if not actual_model.index:
        actual_model.index = get_max_index(actual_model.transformation_mapping) + 1
    if actual_model.index > 1:
        set_index(actual_model, actual_model.index - 1)

    return actual_model


def model_down(*args, **kwargs) -> Model:
    """
    The model_down function is used to move a model down in the list of models
    for a given transformation mapping.  It takes as arguments the primary key
    of the model to be moved and returns that same model after it has been moved.
    The function also takes into account whether or not there are other models with
    the same transformation_mapping, and if so, sets their index values appropriately.

    :param *args: Pass a non-keyworded, variable-length argument list to the function
    :param **kwargs: Pass keyworded variable length of arguments to a function
    :return: The actual model
    :doc-author: Trelent
    """
    actual_model: Model = get_object_or_404(Model, *args, **kwargs)
    models_size = len(
        Model.objects.filter(transformation_mapping=actual_model.transformation_mapping)
    )
    if not actual_model.index:
        actual_model.index = get_max_index(actual_model.transformation_mapping) + 1
    if actual_model.index < models_size:
        set_index(actual_model, actual_model.index + 1)

    return actual_model


def init_main_entity(project: Project) -> int:
    """
    The init_main_entity function is used to determine if the project has a main entity.
    If it does, then we return 1. If not, we return 0.

    :param project:Project: Get the project of the transformation mapping
    :return: The id of the main entity if it exists, otherwise 1
    :doc-author: Trelent
    """
    main_entity = None
    tm = TransformationMapping.objects.filter(project=project).first()
    if tm:
        main_entity = Model.objects.filter(
            transformation_mapping=tm, is_main_entity=1
        ).first()

    return not main_entity if main_entity else 1


def init_index(model: Model):
    """
    The init_index function is a helper function that ensures the index of the transformation
    is unique. If no index is provided, it will be set to one greater than the current maximum
    index in the database.

    :param model:Model: Access the model object
    :return: The maximum index in the transformation_mapping dictionary plus one
    :doc-author: Trelent
    """
    if not model.index or model.index == 0:
        max_index = get_max_index(model.transformation_mapping)
        if not max_index:
            max_index = 0
        model.index = max_index + 1


def unset_main_entity(model: Model) -> None:
    """
    The unset_main_entity function is used to unset the main entity of a transformation mapping.
    It does this by first checking if the model passed in as an argument has been set as the main entity,
    and then proceeds to unset all other models that have been set as the main entities for that same
    transformation mapping. This function is called when a user deletes or updates a model.

    :param model:Model: Access the model class
    :return: None
    :doc-author: Trelent
    """
    if model.is_main_entity:
        # unset all other models to not main entity
        Model.objects.filter(
            transformation_mapping=model.transformation_mapping, is_main_entity=1
        ).update(is_main_entity=0)


def set_new_main_entity(model: Model) -> None:
    """
    The set_new_main_entity function is used to set the main entity of a transformation mapping.
    The function will first check if there is already a main entity, and if not it will set the
    first model in the list as the new main entity. If there are multiple models with no assigned
    main_entity, then it will find which model has been created first and assign that one as new
    main_entity.

    :param model:Model: Get the model of the entity
    :return: None
    :doc-author: Trelent
    """
    main_entity = Model.objects.filter(
        transformation_mapping=model.transformation_mapping, is_main_entity=1
    ).first()
    if not main_entity or main_entity == model:
        # set main entity to the one with the lowest index
        lowest_entity: Model = (
            Model.objects.filter(transformation_mapping=model.transformation_mapping)
            .exclude(pk=model.pk)
            .first()
        )
        if lowest_entity:
            lowest_entity.is_main_entity = 1
            lowest_entity.save()


def get_model_success_url(model: Model) -> str:
    """
    The get_model_success_url function returns the URL of the project_list_model view,
    which is a class-based generic list view that displays all models in a given project.
    The function takes one argument: model, which is an instance of TransformationMapping.
    This function uses reverse to return the URL for this page.

    :param model:Model: Get the primary key of the model
    :return: A string
    :doc-author: Trelent
    """
    return reverse_lazy(
        "project_list_model",
        kwargs={"pk": model.transformation_mapping.project.id},
    )
