import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMessage
from system.models import EmailConfig, SMSConfig
from .models import NoticePool

logger = logging.getLogger('celery.task')


@shared_task
def send_notice_from_pool():
    nps = NoticePool.objects.filter(is_sent=False, send_time__lte=timezone.now()).values_list('id', flat=True).order_by()
    for id in nps:
        send_notice_from_poolid.delay(id)


@shared_task
def send_notice_from_poolid(np_id):
    try:
        np = NoticePool.objects.get(id=np_id)
        np.send()
    except Exception as e:
        logger.error(e)


def send_email(notice_pool: NoticePool) -> tuple[bool, str]:
    email_config = EmailConfig.objects.filter(system__sys_id=notice_pool.sys_id).first()
    if email_config is None:
        raise ValueError('EmailConfig not configured!')
    backend = EmailBackend(
        host=email_config.host,
        port=email_config.port,
        username=email_config.username,
        password=email_config.password,
        use_ssl=email_config.use_ssl,
        use_tls=email_config.use_tls,
        timeout=10,
    )
    to_emails = [user.email for user in notice_pool.send_to.all() if user.email]
    message = EmailMessage(
        subject=notice_pool.title or '通知',
        body=notice_pool.content,
        from_email=email_config.from_email,
        to=to_emails,
        connection=backend,
    )
    try:
        message.send()
        return True, notice_pool.pk
    except Exception as e:
        logger.error(f'send email error: {e}', exc_info=True)
        raise e


@shared_task
def send_sms(np_id) -> None:
    from system.utils.send_sms_message import send_sms_message
    notice_pool = NoticePool.objects.filter(pk=np_id).first()
    if notice_pool is None:
        raise ValueError('NoticePool not found!')
    sms_config = SMSConfig.objects.filter(system__sys_id=notice_pool.sys_id, is_enabled=True).first()
    if sms_config is None:
        notice_pool.is_sent = False
        notice_pool.error_message = 'SMSConfig not configured!'
        notice_pool.save()
        raise ValueError('SMSConfig not configured!')
    for user in notice_pool.send_to.filter(mobile__isnull=False):
        try:
            send_sms_message(notice_pool.sys_id, user.mobile, notice_pool.content)
        except Exception as e:
            logger.error('send_sms_message error', exc_info=e)
