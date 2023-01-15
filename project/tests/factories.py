from collections.abc import Sequence
from typing import Any

import factory
from django.contrib.auth import get_user_model
from factory import Faker, post_generation
from factory.django import DjangoModelFactory

from project.models import Project, TransformationMapping, Model, Field


class UserFactory(DjangoModelFactory):

    username = Faker("user_name")
    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    user = factory.SubFactory(UserFactory)
    name = Faker("bs")
    # faker.providers.python.Provider.pystr(min_chars=4, max_chars=20)
    description = Faker("paragraph")


class TransformationMappingFactory(DjangoModelFactory):
    class Meta:
        model = TransformationMapping

    project = factory.SubFactory(ProjectFactory)


class ModelFactory(DjangoModelFactory):
    class Meta:
        model = Model

    transformation_mapping = factory.SubFactory(TransformationMappingFactory)

    name = Faker("bs")
    description = Faker("paragraph")
    is_main_entity = Faker("pybool")
    index = Faker("pyint", min_value=1, max_value=20)


class FieldFactory(DjangoModelFactory):
    class Meta:
        model = Field

    model = factory.SubFactory(ModelFactory)

    name = Faker("bs")
    description = Faker("paragraph")
    index = Faker("pyint", min_value=1, max_value=20)
