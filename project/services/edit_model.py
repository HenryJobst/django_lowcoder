from django.db.models import Max
from django.shortcuts import get_object_or_404

from project.models import Model, TransformationMapping


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
