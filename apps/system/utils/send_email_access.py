import logging
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMessage
from system.models import EmailConfig

logger = logging.getLogger('restapi')


def send_email_access(sys_id: int, to: str, code: str) -> tuple[bool, str]:
    email_config = EmailConfig.objects.filter(system__sys_id=sys_id).first()
    if email_config is None:
        raise SystemError('EmailConfig not configured!')
    backend = EmailBackend(
        host=email_config.host,
        port=email_config.port,
        username=email_config.username,
        password=email_config.password,
        use_ssl=email_config.use_ssl,
        use_tls=email_config.use_tls,
        timeout=10,
    )
    title_prefix = email_config.title_prefix or ''
    message = EmailMessage(
        subject=title_prefix + '验证码',
        body=f'您的验证码是：{code}, 5分钟内有效',
        from_email=email_config.from_email,
        to=[to],
        connection=backend,
    )
    try:
        message.send()
        return True, code
    except Exception as e:
        logger.error(f'send email error: {e}', exc_info=True)
        return False, str(e)
