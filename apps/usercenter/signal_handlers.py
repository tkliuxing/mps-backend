from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from system.models import SystemLog
from utility.client_ip import get_client_ip


@receiver(user_logged_in)
def add_user_login_log(sender, request, user, **kwargs):
    SystemLog.objects.create(
        sys_id=user.sys_id,
        org_id=user.org_id,
        log_level=0,
        log_type='登录日志',
        user=user, user_name=user.username,
        content=get_client_ip(request),
    )
