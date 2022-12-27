from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from project.models import Model, TransformationMapping, Project, Field


def set_index(model: Model | Field, index: int) -> None:
    """
    The set_index function is a helper function that allows us to change the index of a model.
    It does this by first checking if there are any other models with the same transformation_mapping and index,
    and if so, it switches their indexes. If not, it simply saves the model with its new index.

    :param model:Model: Specify the model that is being modified
    :param index:int: Indicate which index the model should be saved with
    :return: None
    :doc-author: Trelent
    """
    other_model = (
        Model.objects.filter(
            transformation_mapping=model.transformation_mapping,
            index=index,
        ).first()
        if isinstance(model, Model)
        else Field.objects.filter(model=model.model, index=index).first()
    )
    if other_model:
        switch_index(model, other_model)
    else:
        save_with_index(model, index)


def save_with_index(model: Model | Field, index: int) -> int:
    """
    The save_with_index function is a helper function that allows us to save the model with an index.
    It also returns the old index of the model, so we can reset it later.

    :param model:Model|Field: Specify the model that is being saved
    :param index:int: Specify the index of the model in a list
    :return: The old index of the model
    :doc-author: Trelent
    """
    old_index = model.index
    model.index = index
    model.save()
    return old_index


def switch_index(actual_entity: Model | Field, other_entity: Model | Field) -> None:
    """
    The switch_index function is used to switch the index of two models.
    It does this by temporarily setting other_entity.index to max used index + 1
    to not violate unique constraint on index, then sets actual_model.index = other_entity.index, and finally sets
    other_entity.index = actual_model's previous value.

    :param actual_entity:Model|Field: Determine whether the switch_index function is called on a model or field
    :param other_entity:Model|Field: Determine the type of the model that is passed to this function
    :return: None
    :doc-author: Trelent
    """
    # temporarily set other_entity.index to max used index + 1 to not violate unique constraint on index
    max_index = (
        get_max_index(actual_entity.transformation_mapping)
        if isinstance(actual_entity, Model)
        else get_max_field_index(actual_entity.model)
    )
    other_model_index = save_with_index(other_entity, max_index + 1)
    actual_model_index = save_with_index(actual_entity, other_model_index)
    save_with_index(other_entity, actual_model_index)


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


def get_max_field_index(model: Model) -> int:
    """
    The get_max_field_index function returns the maximum index of all fields in a model.

    :param model:Model: Get the fields for that model
    :return: The maximum index of all fields in the model
    :doc-author: Trelent
    """
    return Field.objects.filter(model=model).aggregate(max=Max("index")).get("max", 0)


def model_up(*args, **kwargs) -> Model:
    """
    The model_up function takes a model as an argument and sets its index to the next highest integer.
    If the model has no index, it assigns it one. If the model's index is greater than 1,
    it decrements that value by 1.

    :param *args: Pass a non-keyworded, variable-length argument list to the function
    :param **kwargs: Pass a keyworded, variable-length argument list
    :return: The model that is up in the transformation mapping
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
    The function also takes into account whether there are other models with
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


def field_up(*args, **kwargs) -> Field:
    """
    The field_up function takes a field and moves it up one position in the list of fields.
    If the field is already at the top of the list, nothing happens.

    :param *args: Pass a variable number of arguments to a function
    :param **kwargs: Pass keyworded variable length of arguments to a function
    :return: The field that is one index higher than the given field
    :doc-author: Trelent
    """
    actual_field: Field = get_object_or_404(Field, *args, **kwargs)
    if not actual_field.index:
        actual_field.index = get_max_field_index(actual_field.model) + 1
    if actual_field.index > 1:
        set_index(actual_field, actual_field.index - 1)

    return actual_field


def field_down(*args, **kwargs) -> Field:
    """
    The field_down function moves the field with the given pk down one position in
    the list of fields for its model. If it is already at the bottom of that list, it
    does nothing.

    :param *args: Pass a variable number of arguments to a function
    :param **kwargs: Pass keyworded variable length of arguments to a function
    :return: The field that is located below the given field
    :doc-author: Trelent
    """
    actual_field: Field = get_object_or_404(Field, *args, **kwargs)
    fields_size = len(Field.objects.filter(model=actual_field.model))
    if not actual_field.index:
        actual_field.index = get_max_field_index(actual_field.model) + 1
    if actual_field.index < fields_size:
        set_index(actual_field, actual_field.index + 1)

    return actual_field


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


def init_index(entity: Model | Field):
    """
    The init_index function is used to assign an index value to a model or field.
    If the entity does not have an index assigned, it will be set equal to the maximum
    index of either its transformation mapping's models or its parent model's fields plus 1.


    :param entity:Model|Field: Determine whether the function is called for a model or field
    :return: The index of the entity
    :doc-author: Trelent
    """
    if not entity.index or entity.index == 0:
        max_index = (
            get_max_index(entity.transformation_mapping)
            if isinstance(entity, Model)
            else get_max_field_index(entity.model)
        )
        if not max_index:
            max_index = 0
        entity.index = max_index + 1


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


# noinspection PyUnusedLocal
def get_models_or_next_url(self: object, next_url: str, pk: int) -> str:
    return (
        next_url if next_url else reverse_lazy("project_list_models", kwargs={"pk": pk})
    )


# noinspection PyUnusedLocal
def get_model_edit_or_next_url(self: object, next_url: str, pk: int) -> str:
    return (
        next_url
        if next_url
        else reverse_lazy("project_detail_model", kwargs={"pk": pk})
    )


def get_model_edit_or_next_url_p(self: object, next_url: str, model: Model) -> str:
    return get_model_edit_or_next_url(self, next_url, model.id)


# noinspection PyUnusedLocal
def get_fields_or_next_url(self: object, next_url: str, pk: int) -> str:
    return (
        next_url if next_url else reverse_lazy("project_list_fields", kwargs={"pk", pk})
    )


# noinspection PyUnusedLocal
def get_field_edit_or_next_url(self: object, next_url: str, pk: int) -> str:
    return (
        next_url
        if next_url
        else reverse_lazy("project_update_field", kwargs={"pk": pk})
    )


def get_field_edit_or_next_url_p(self: object, next_url: str, field: Field) -> str:
    return get_model_edit_or_next_url(self, next_url, field.id)
