import logging
import requests
from system.models import SMSConfig
from .smslogger import sms_logger

logger = logging.getLogger('restapi')


def send_phone_access(config: SMSConfig, phone, code) -> (bool, int):
    url = getattr(config, 'post_url')
    phoneNumbers = phone
    content = code
    headers = {
        "Content-Type": "application/json"
    }
    resp = requests.post(url, headers=headers, json={'phoneNumbers': phoneNumbers.split(','), 'content': content})
    return True, code


def send_sms_message(config: SMSConfig, phone, content) -> None:
    url = getattr(config, 'post_url')
    phoneNumbers = phone
    headers = {
        "Content-Type": "application/json"
    }
    requests.post(url, headers=headers, json={'phoneNumbers': phoneNumbers.split(','), 'content': content})
