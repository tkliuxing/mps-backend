from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class MyJSONWebTokenAuthentication(JSONWebTokenAuthentication):

    def authenticate_credentials(self, payload):
        User = get_user_model()
        user_id = payload.get('user_id')

        if not user_id:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user
