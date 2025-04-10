try:
    from .sms_tencent import send_sms_message as sms_tencent
except ImportError:
    sms_tencent = None

try:
    from .sms_juhe import send_sms_message as sms_juhe
except ImportError:
    sms_juhe = None

try:
    from .sms_jhsl import send_sms_message as sms_jhsl
except ImportError:
    sms_jhsl = None

from system.models import System, SMSConfig


def send_sms_message(sys_id: int, phone, message) -> None:
    system = System.objects.get(sys_id=sys_id)
    sms_config = SMSConfig.objects.filter(system=system, is_enabled=True).first()
    if sms_config is None:
        raise SystemError('SMSConfig not configured!')
    if sms_config.sms_type == 'TENCENT':
        if not sms_tencent:
            raise SystemError('TENCENT SMS ImportError!')
        return sms_tencent(sms_config, phone, message)
    if sms_config.sms_type == 'JUHE':
        if not sms_juhe:
            raise SystemError('JUHE SMS ImportError!')
        return sms_juhe(sms_config, phone, message)
    if sms_config.sms_type == 'JHSL':
        if not sms_jhsl:
            raise SystemError('JUHE SMS ImportError!')
        return sms_jhsl(sms_config, phone, message)

    raise SystemError('sms_type not configured!')
