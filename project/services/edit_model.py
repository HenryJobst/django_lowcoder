from django.db.models import Max
from django.shortcuts import get_object_or_404

from project.models import Model


def model_up(*args, **kwargs) -> int:
    actual_model: Model = get_object_or_404(Model, *args, **kwargs)
    actual_index: int = actual_model.index
    if actual_index > 1:
        other_model = Model.objects.filter(
            transformation_mapping=actual_model.transformation_mapping,
            index=actual_index - 1,
        ).first()
        if other_model:
            max_index = (
                Model.objects.filter(
                    transformation_mapping=actual_model.transformation_mapping
                )
                .aggregate(max=Max("index"))
                .get("max", 0)
            )
            actual_model.index = other_model.index
            other_model.index = max_index + 1
            other_model.save()
            actual_model.save()
            other_model.index = actual_index
            other_model.save()
        else:
            actual_model.index = actual_index - 1
            actual_model.save()

    return actual_model.transformation_mapping.project.id


def model_down(pk: int):
    actual_model: Model = get_object_or_404(Model, args=[], kwargs={"pk": pk})
    actual_index: int = actual_model.index
    models_size = len(
        Model.objects.filter(transformation_mapping=actual_model.transformation_mapping)
    )
    if actual_index < models_size:
        other_model = Model.objects.filter(
            transformation_mapping=actual_model.transformation_mapping,
            index=actual_index + 1,
        ).first()
        if other_model:
            actual_model.index = other_model.index
            other_model.index = actual_index
            actual_model.save()
            other_model.save()
