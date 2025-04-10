import logging
import requests
from system.models import SMSConfig
from .smslogger import sms_logger

logger = logging.getLogger('restapi')


def send_phone_access(config: SMSConfig, phone, code) -> (bool, int):
    url = getattr(config, 'post_url')
    appkey = getattr(config, 'app_key')
    tpl_id = getattr(config, 'template_id')
    if not any([url, appkey, tpl_id]):
        logger.error('短信验证码配置错误')
        return False, 400
    params = {'mobile': phone, 'tpl_id': tpl_id, 'tpl_value': '#code#=' + code, 'key': appkey}
    ret = requests.get(url, params)
    ret_json = ret.json()
    if ret_json.get('error_code') == 0:
        logger.info('短信发送成功 code: {}'.format(code))
        sms_logger(config, phone, code)
        return True, code
    else:
        logger.error('短信验证码错误', exc_info=ret_json)
        return False, code


def send_sms_message(config: SMSConfig, phone, message) -> None:
    url = getattr(config, 'post_url')
    appkey = getattr(config, 'app_key')
    tpl_id = getattr(config, 'template_id')
    if not any([url, appkey, tpl_id]):
        logger.error('短信验证码配置错误')
        raise ValueError('短信验证码配置错误')
    params = {'mobile': phone, 'tpl_id': tpl_id, 'tpl_value': '#message#=' + message, 'key': appkey}
    ret = requests.get(url, params)
    ret_json = ret.json()
    if ret_json.get('error_code') == 0:
        logger.info('短信发送成功 message: {}'.format(message))
        sms_logger(config, phone, message)
    else:
        logger.error('短信验证码错误', exc_info=ret_json)
        raise ValueError(f'短信验证码错误【{params}】: {ret.content}')
