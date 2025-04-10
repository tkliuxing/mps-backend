from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


UserModel = get_user_model()


class UserAuthBackend(ModelBackend):

    def _get_user_permissions(self, user_obj, obj=None):
        return user_obj.get_permissions()

    def _get_group_permissions(self, user_obj, obj=None):
        from usercenter.models import FuncPermission
        return FuncPermission.objects.filter(funcgroup__user=user_obj)

    def _get_permissions(self, user_obj, obj, from_name):
        """
        Return the permissions of `user_obj` from `from_name`. `from_name` can
        be either "group" or "user" to return permissions from
        `_get_group_permissions` or `_get_user_permissions` respectively.
        """
        from usercenter.models import FuncPermission
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_%s_perm_cache' % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = FuncPermission.objects.all()
            else:
                perms = getattr(self, '_get_%s_permissions' % from_name)(user_obj)
            perms = perms.values_list('codename', flat=True).order_by()
            setattr(user_obj, perm_cache_name, set(perms))
        return getattr(user_obj, perm_cache_name)

    def authenticate(self, request, username=None, password=None, sys_id=None, **kwargs):
        if sys_id is None:
            sys_id = 0
        try:
            user = UserModel.objects.get(username=username, sys_id=sys_id)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

