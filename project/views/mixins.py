from django.contrib.auth.mixins import UserPassesTestMixin


class ModelUserFieldPermissionMixin(UserPassesTestMixin):
    model_permission_user_field = 'user'
    slug_url_kwarg = "slug"
    pk_url_kwarg = "pk"

    def get_model_permission_user_field(self):
        return self.model_permission_user_field

    def test_func(self):
        model_attr = self.get_model_permission_user_field()
        current_user = self.request.user

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk or slug:
            return current_user == getattr(self.get_object(), model_attr)

        return current_user == getattr(self.get_queryset().first(),
                                       model_attr)
