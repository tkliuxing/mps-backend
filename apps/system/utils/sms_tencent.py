
import logging
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20190711 import sms_client
from tencentcloud.sms.v20190711 import models as sms_models
from system.models import SMSConfig
from .smslogger import sms_logger

logger = logging.getLogger('restapi')


def send_phone_access(config: SMSConfig, phone, code) -> (bool, int):
    if config is None:
        raise SystemError('该系统的短信配置不存在！')
    secret_id = getattr(config, 'tencent_cloud_secretid')
    secret_key = getattr(config, 'tencent_cloud_secretkey')
    sms_appid = getattr(config, 'app_id')
    sms_tplid = getattr(config, 'template_id')
    sms_tpl_sign = getattr(config, 'template_sign')
    if not secret_id or not secret_key:
        logger.error('TENCENT CLOUD 配置错误')
        return False, 400
    if not sms_appid or not sms_tplid or not sms_tpl_sign:
        logger.error('TENCENT SMS 配置错误')
        return False, 400
    try:
        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = "sms.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = sms_client.SmsClient(cred, "", client_profile)
        req = sms_models.SendSmsRequest()
        req.SmsSdkAppid = sms_appid
        req.Sign = sms_tpl_sign
        req.ExtendCode = ""
        req.SenderId = ""
        req.PhoneNumberSet = ["+86" + phone]
        req.TemplateID = sms_tplid
        req.TemplateParamSet = [code]
        resp = client.SendSms(req)
        if resp.SendStatusSet[0].Code != 'Ok':
            logger.error(resp.to_json_string())
            return False, 400
        sms_logger(config, phone, code)
        return True, code
    except TencentCloudSDKException as e:
        logger.error(e)
        return False, 400


def send_sms_message(config: SMSConfig, phone, message) -> None:
    if config is None:
        raise SystemError('该系统的短信配置不存在！')
    secret_id = getattr(config, 'tencent_cloud_secretid')
    secret_key = getattr(config, 'tencent_cloud_secretkey')
    sms_appid = getattr(config, 'app_id')
    sms_tplid = getattr(config, 'template_id')
    sms_tpl_sign = getattr(config, 'template_sign')
    if not secret_id or not secret_key:
        logger.error('TENCENT CLOUD 配置错误')
        raise ValueError('TENCENT CLOUD 配置错误')
    if not sms_appid or not sms_tplid or not sms_tpl_sign:
        logger.error('TENCENT SMS 配置错误')
        raise ValueError('TENCENT SMS 配置错误')
    try:
        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = "sms.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = sms_client.SmsClient(cred, "", client_profile)
        req = sms_models.SendSmsRequest()
        req.SmsSdkAppid = sms_appid
        req.Sign = sms_tpl_sign
        req.ExtendCode = ""
        req.SenderId = ""
        req.PhoneNumberSet = ["+86" + phone]
        req.TemplateID = sms_tplid
        req.TemplateParamSet = [message]
        resp = client.SendSms(req)
        if resp.SendStatusSet[0].Code != 'Ok':
            logger.error(resp.to_json_string())
            raise ValueError('TENCENT send_sms_message SendStatus not OK!')
        sms_logger(config, phone, message)
    except TencentCloudSDKException as e:
        logger.error(e, exc_info=e)
        raise e
