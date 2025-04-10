import json
import logging
import redis

from pypinyin import pinyin, Style
from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError
from django_redis import get_redis_connection
from wechatpy import WeChatClientException
from wechatpy.client import WeChatClient
from wechatpy.session.redisstorage import RedisStorage

from system.utils.wechat import get_wechat_config
from system.models import WechatConfig

from baseconfig.models import BaseConfigFileUpload


logger = logging.getLogger('restapi')


class JSONField(serializers.Field):

    def to_internal_value(self, data):
        try:
            return json.dumps(data)
        except (TypeError, ValueError):
            self.fail('invalid')

    def to_representation(self, value):
        return json.loads(value)


class WechatJsSign(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True)
    url = serializers.CharField(required=True, write_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class WechatAppPhoneNumSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True)
    code = serializers.CharField(required=True, write_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class WechatAppQrCodeSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True)
    scene = serializers.CharField(required=True, write_only=True)
    page = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PinYinSerializer(serializers.Serializer):
    origin_string = serializers.CharField(write_only=True, label='字符串', max_length=64, help_text='字符串')
    pinyin = serializers.ListSerializer(
        child=serializers.CharField(), label='拼音数组', read_only=True, help_text='拼音数组'
    )

    def create(self, validated_data):
        data = {
            'pinyin': []
        }
        py = pinyin(validated_data['origin_string'], style=Style.NORMAL)
        data['pinyin'] = list(map(lambda x: x[0], py))
        return data

    def update(self, instance, validated_data):
        pass


class MPTemplateMsgSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True, help_text='系统ID')
    appid = fields.CharField(required=False, allow_null=True, allow_blank=True, write_only=True, help_text='公众号APPID')
    touser = fields.CharField(required=True, write_only=True, help_text='接收人openid')
    template_id = fields.CharField(required=True, write_only=True, help_text='模板消息模板ID')
    url = fields.CharField(required=False, write_only=True, allow_null=True, allow_blank=True, help_text='模板消息跳转URL')
    data = fields.JSONField(required=True, write_only=True, help_text='模板消息内容字段数据')

    errcode = fields.CharField(read_only=True, help_text='微信错误码,正常返回 0')
    errmsg = fields.CharField(read_only=True, help_text='微信错误信息,正常返回 ok')

    def validate(self, data):
        appid = data.get('appid', '')
        sys_id = data['sys_id']
        try:
            wechat_config = get_wechat_config(sys_id, mp_aid=appid)  # type: WechatConfig
        except ValueError:
            raise ValidationError('微信公众号未配置')
        redis_client = get_redis_connection("default")
        session_interface = RedisStorage(
            redis_client,
            prefix="wechatpy"
        )
        appid = getattr(wechat_config, 'mp_aid')
        secret = getattr(wechat_config, 'mp_sk')
        if not appid or not secret:
            raise ValidationError('微信公众号未配置')
        wechat_client = WeChatClient(
            appid,
            secret,
            session=session_interface
        )
        data['wechat_client'] = wechat_client
        return data

    def create(self, validated_data):
        wechat_client = validated_data.pop('wechat_client')  # type: WeChatClient
        try:
            resp = wechat_client.message.send_template(
                validated_data['touser'],
                validated_data['template_id'],
                validated_data['data'],
                validated_data.get('url') or None,
            )
        except WeChatClientException as e:
            resp = {
                'errcode': e.errcode,
                'errmsg': e.errmsg
            }
        return resp

    def update(self, instance, validated_data):
        return {}

    def to_representation(self, instance):
        return instance


class WXATemplateMsgSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True, help_text='系统ID')
    appid = fields.CharField(required=False, allow_null=True, allow_blank=True, write_only=True, help_text='小程序APPID')
    touser = fields.CharField(required=True, write_only=True, help_text='接收人openid')
    template_id = fields.CharField(required=True, write_only=True, help_text='模板消息模板ID')
    page = fields.CharField(required=False, write_only=True, allow_null=True, allow_blank=True, help_text='消息跳转page')
    data = fields.JSONField(required=True, write_only=True, help_text='模板消息内容字段数据')

    errcode = fields.CharField(read_only=True, help_text='微信错误码,正常返回 0')
    errmsg = fields.CharField(read_only=True, help_text='微信错误信息,正常返回 ok')

    def validate(self, data):
        appid = data.get('appid', '')
        sys_id = data['sys_id']
        try:
            wechat_config = get_wechat_config(sys_id, wxa_aid=appid)  # type: WechatConfig
        except ValueError:
            raise ValidationError('微信小程序未配置')
        redis_client = get_redis_connection("default")
        session_interface = RedisStorage(
            redis_client,
            prefix="wechatpy"
        )
        appid = getattr(wechat_config, 'wxa_aid')
        secret = getattr(wechat_config, 'wxa_sk')
        if not appid or not secret:
            raise ValidationError('微信小程序未配置')
        wechat_client = WeChatClient(
            appid,
            secret,
            session=session_interface
        )
        data['wechat_client'] = wechat_client
        return data

    def create(self, validated_data):
        wechat_client = validated_data.pop('wechat_client')  # type: WeChatClient
        try:
            resp = wechat_client.wxa.send_subscribe_message(
                validated_data['touser'],
                validated_data['template_id'],
                validated_data['data'],
                validated_data.get('page') or None,
            )
        except WeChatClientException as e:
            resp = {
                'errcode': e.errcode,
                'errmsg': e.errmsg
            }
        return resp

    def update(self, instance, validated_data):
        return {}

    def to_representation(self, instance):
        return instance


class SMSSendCodeSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True, help_text='系统ID')
    org_id = serializers.IntegerField(required=False, allow_null=True, write_only=True, help_text='机构ID')
    phone = serializers.CharField(required=True, write_only=True, help_text='手机号码')
    expire_seconds = serializers.IntegerField(required=False, allow_null=True, write_only=True, help_text='超时时长')

    def create(self, validated_data):
        import random
        from datetime import timedelta
        from django.utils import timezone
        from system.models import SMSLog
        from system.utils.send_phone_access import send_phone_access
        code = "".join(random.choices("1234567890", k=6))
        sys_id = validated_data['sys_id']
        org_id = validated_data.get('org_id')
        phone = validated_data['phone']
        expire_seconds = validated_data.get('expire_seconds')

        if SMSLog.objects.filter(
            sys_id=sys_id,
            phone=phone,
            create_time__gt=(timezone.now() - timedelta(seconds=60))
        ):
            return {
                'errcode': 2,
                'errmsg': '不可频繁发送',
            }

        try:
            success, _ = send_phone_access(sys_id, phone, code)
        except SystemError as e:
            return {
                'errcode': 1,
                'errmsg': str(e),
            }
        if not success:
            return {
                'errcode': 1,
                'errmsg': '发送失败',
            }
        SMSLog.objects.create(
            sys_id=sys_id,
            org_id=org_id,
            phone=phone,
            content=code,
            expire_seconds=expire_seconds,
        )
        return {
            'errcode': 0,
            'errmsg': 'ok',
        }

    def update(self, instance, validated_data):
        pass


class SMSCodeValidSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True, help_text='系统ID')
    org_id = serializers.IntegerField(required=False, allow_null=True, write_only=True, help_text='机构ID')
    phone = serializers.CharField(required=True, write_only=True, help_text='手机号码')
    code = serializers.CharField(required=True, write_only=True, help_text='手机验证码')

    def create(self, validated_data):
        from system.models import SMSLog
        sys_id = validated_data['sys_id']
        org_id = validated_data.get('org_id')
        phone = validated_data['phone']
        code = validated_data['code']
        sms_logs = SMSLog.objects.filter(
            sys_id=sys_id,
            org_id=org_id,
            phone=phone,
            content=code,
        )
        for l in sms_logs:
            if not l.is_expire:
                SMSLog.objects.filter(
                    sys_id=sys_id,
                    org_id=org_id,
                    phone=phone,
                ).delete()
                return {
                    'errcode': 0,
                    'errmsg': 'ok',
                }
        return {
            'errcode': 1,
            'errmsg': '验证失败',
        }

    def update(self, instance, validated_data):
        pass
