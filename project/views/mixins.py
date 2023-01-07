from django.contrib.auth.mixins import UserPassesTestMixin


class ModelUserFieldPermissionMixin(UserPassesTestMixin):
    model_permission_user_field = "user"

    def get_model_permission_user_field(self):
        return self.model_permission_user_field

    # noinspection PyUnresolvedReferences
    def test_func(self):
        current_user = self.request.user

        model_object = self.get_object()
        user_holder = self.get_user_holder(model_object)

        model_attr = self.get_model_permission_user_field()
        return current_user.is_superuser or current_user == getattr(
            user_holder, model_attr
        )

    # noinspection PyMethodMayBeStatic
    def get_user_holder(self, model_object):
        return model_object
