import datetime
import logging
import random
import time
import uuid
import json

import redis
from django.contrib.auth.signals import user_logged_in
from django_redis import get_redis_connection
from wechatpy import WeChatClientException
from wechatpy.oauth import WeChatOAuth, WeChatOAuthException
from wechatpy.client import WeChatClient
from wechatpy.session.redisstorage import RedisStorage
from rest_captcha.serializers import RestCaptchaSerializer
from rest_framework import serializers, fields
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings

from system.utils.wechat import get_wechat_config
from system.models import WechatConfig
from .models import PhoneAccess, User, EmailAccess

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
logger = logging.getLogger('restapi')
QR_LOGIN_EXP_TIME_SEC = 60 * 5


def next_username(sys_id):
    import random
    from django.db.models import Max
    user_count = User.objects.filter(sys_id=sys_id).count()
    id_max = User.objects.filter(sys_id=sys_id).aggregate(id_max=Max('id'))['id_max']
    base_chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    rand_chars = ''.join(random.sample(base_chars, 4))
    if user_count:
        return f"用户{rand_chars}{id_max[-4:]}_{user_count:07d}"
    else:
        user_count = 1
        return f"用户{rand_chars}{id_max[-4:]}_{user_count:07d}"


def user_login(request: Request, user: User) -> bytes:
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    return token


class PhoneAuthenticationSerializer(serializers.Serializer):
    sys_id = fields.IntegerField(help_text='sys_id', required=True)
    phone = fields.CharField(required=True, help_text='手机号')
    phone_access = fields.CharField(required=True, help_text='验证码')

    def validate(self, data):
        sys_id, phone, pa = data['sys_id'], data['phone'], data['phone_access']
        try:
            access = PhoneAccess.objects.get(phone=phone, phone_access=pa, sys_id=sys_id)
            if phone != '17704818161':
                access.delete()
        except PhoneAccess.DoesNotExist:
            raise ValidationError('验证码错误')
        try:
            data['user'] = User.objects.filter(sys_id=sys_id).get(mobile=phone)
            if not data['user'].is_active:
                msg = '该用户已停用'
                raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        return data

    def create(self, validated_data):
        user = validated_data['user']
        token = user_login(self.context['request'], user)
        response = {'token': token}
        return response

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class PhoneAccessSerializer(serializers.Serializer):
    sys_id = fields.IntegerField(help_text='sys_id', required=True)
    phone = fields.CharField(label='手机号', help_text='手机号')
    error = fields.CharField(read_only=True)

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        pass


class PhoneAccessValidateSerializer(serializers.Serializer):
    sys_id = fields.IntegerField(help_text='sys_id', required=True)
    phone = fields.CharField(label='手机号', help_text='手机号', required=True)
    phone_access = fields.CharField(label='验证码', help_text='验证码', required=True)

    def validate(self, data):
        sys_id, phone, pa = data['sys_id'], data['phone'], data['phone_access']
        try:
            access = PhoneAccess.objects.get(phone=phone, phone_access=pa, sys_id=sys_id)
            if phone != '17704818161':
                access.delete()
        except PhoneAccess.DoesNotExist:
            raise ValidationError('验证码错误')
        return data

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        pass


class EmailAccessSerializer(serializers.Serializer):
    sys_id = fields.IntegerField(help_text='sys_id', required=True)
    email = fields.EmailField(label='邮箱', help_text='邮箱', required=True)

    def validate(self, data):
        from system.utils.send_email_access import send_email_access
        sys_id, email = data['sys_id'], data['email']
        now = datetime.datetime.now()
        try:
            access = EmailAccess.objects.get(email=email, sys_id=sys_id)
        except EmailAccess.DoesNotExist:
            access = EmailAccess(email=email, sys_id=sys_id)
        except EmailAccess.MultipleObjectsReturned:
            EmailAccess.objects.filter(email=email, sys_id=sys_id).delete()
            access = EmailAccess(email=email, sys_id=sys_id)
        if access.email_access and access.create_time > now - datetime.timedelta(seconds=60):
            raise ValidationError('请勿短时间重复发送')
        code = "".join(random.choices("1234567890", k=6))
        success, resp = send_email_access(sys_id, email, code)
        logger.info('send email: {} - {}'.format(success, resp))
        if not success:
            raise ValidationError('邮件发送失败')
        access.email_access = code
        access.save()
        return data

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        pass


class EmailAccessValidateSerializer(serializers.Serializer):
    sys_id = fields.IntegerField(help_text='sys_id', required=True)
    email = fields.EmailField(label='邮箱', help_text='邮箱', required=True)
    email_access = fields.CharField(label='验证码', help_text='验证码', required=True)

    def validate(self, data):
        sys_id, email, pa = data['sys_id'], data['email'], data['email_access']
        try:
            access = EmailAccess.objects.get(email=email, email_access=pa, sys_id=sys_id)
        except EmailAccess.DoesNotExist:
            raise ValidationError('验证码错误')
        return data

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        pass


class EmailLoginSerializer(serializers.Serializer):
    sys_id = fields.IntegerField(help_text='sys_id', required=True, write_only=True)
    email = fields.EmailField(label='邮箱', help_text='邮箱', required=True, write_only=True)
    email_access = fields.CharField(label='验证码', help_text='验证码', required=True, write_only=True)
    token = fields.CharField(read_only=True, help_text='token')

    def validate(self, data):
        sys_id, email, pa = data['sys_id'], data['email'], data['email_access']
        try:
            access = EmailAccess.objects.get(email=email, email_access=pa, sys_id=sys_id)
        except EmailAccess.DoesNotExist:
            raise ValidationError('验证码错误')
        try:
            user = User.objects.get(email=email, sys_id=sys_id, is_active=True)
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        except User.MultipleObjectsReturned:
            raise ValidationError('邮箱错误')
        except Exception as e:
            logger.exception(f'邮箱登录错误: {sys_id} {email} {pa} {e}')
            raise ValidationError('Error')
        access.delete()
        data['user'] = user
        return data

    def create(self, validated_data):
        token = user_login(self.context['request'], validated_data['user'])
        response = {'token': token.decode() if isinstance(token, bytes) else token}
        return response

    def update(self, instance, validated_data):
        return self.create(validated_data)


class MyJSONWebTokenSerializer(JSONWebTokenSerializer):
    sys_id = serializers.IntegerField(default=1)
    org_id = serializers.IntegerField(required=False, allow_null=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def is_valid(self):
        is_valid = super().is_valid()
        if is_valid:
            user = self.object.get('user')
            if user:
                user_logged_in.send(sender=user.__class__, request=self.context['request'], user=user)
        return is_valid

    def validate(self, attrs):
        org_id = attrs.get('org_id')
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password'),
            'sys_id': attrs.get('sys_id')
        }

        if all([credentials[self.username_field], credentials['password']]) and credentials['sys_id'] is not None:
            params = {
                'username': credentials[self.username_field],
                'sys_id': credentials['sys_id']
            }
            if org_id:
                params['org_id'] = org_id
            try:
                user = User.objects.get(**params)
            except User.DoesNotExist:
                msg = '用户名或密码错误1'
                raise serializers.ValidationError(msg)

            if not user.check_password(credentials['password']):
                msg = '用户名或密码错误2'
                raise serializers.ValidationError(msg)

            if user:
                if not user.is_active:
                    msg = '该用户已停用'
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = '用户名或密码错误3'
                raise serializers.ValidationError(msg)
        else:
            msg = '参数错误'
            raise serializers.ValidationError(msg)


class CaptchaLoginSerializer(RestCaptchaSerializer, MyJSONWebTokenSerializer):
    def is_valid(self):
        return MyJSONWebTokenSerializer.is_valid(self)

    def validate(self, attrs):
        try:
            RestCaptchaSerializer.validate(self, attrs)
        except serializers.ValidationError as e:
            if '用户名或密码错误' in str(e):
                raise e
            if '该用户已停用' in str(e):
                raise e
            raise serializers.ValidationError('验证码错误')
        return MyJSONWebTokenSerializer.validate(self, attrs)


class WXALoginSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True, help_text='系统ID')
    code = fields.CharField(required=True, write_only=True, help_text='临时登录凭证code')
    appid = fields.CharField(required=False, allow_null=True, allow_blank=True, write_only=True, help_text='小程序APPID')
    token = fields.CharField(read_only=True, help_text='用户访问令牌')

    def validate(self, data):
        code = data['code']
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
        try:
            data = wechat_client.wxa.code_to_session(code)
        except WeChatClientException as e:
            logger.exception('微信错误: sys_id {} appid {}---{}---'.format(sys_id, appid, str(e)))
            raise ValidationError('code已使用')
        openid = data['openid']
        try:
            user = User.objects.get(wxa_oid=openid, sys_id=sys_id)
            if not user.is_active:
                msg = '该用户已停用'
                raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            logger.exception(f'用户不存在: {sys_id}: {openid}')
            raise ValidationError('用户不存在')
        return {'user': user}

    def create(self, validated_data):
        token = user_login(self.context['request'], validated_data['user'])
        response = {'token': token}
        return response

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class WXARegLoginSerializer(WXALoginSerializer):
    sys_id = serializers.IntegerField(required=True, write_only=True, help_text='系统ID')
    org_id = fields.IntegerField(help_text='org_id', write_only=True, required=True)
    code = fields.CharField(required=True, write_only=True, help_text='临时登录凭证code')
    appid = fields.CharField(required=False, allow_null=True, allow_blank=True, write_only=True, help_text='小程序APPID')
    token = fields.CharField(read_only=True, help_text='用户访问令牌')

    def validate(self, data):
        code = data['code']
        appid = data.get('appid', '')
        sys_id = data['sys_id']
        org_id = data['org_id']
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
        try:
            data = wechat_client.wxa.code_to_session(code)
        except WeChatClientException:
            logger.exception('微信错误: sys_id {} appid {}---{}---'.format(sys_id, appid, code))
            raise ValidationError('code已使用')
        try:
            user = User.objects.get(wxa_oid=data['openid'], sys_id=sys_id)
            if not user.is_active:
                msg = '该用户已停用'
                raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            username = next_username(sys_id)
            user = User.objects.create_user(
                username=username, password=str(time.time()),
                full_name=username,
                sys_id=sys_id, org_id=org_id, wxa_oid=data['openid']
            )
        return {'user': user}

    def create(self, validated_data):
        token = user_login(self.context['request'], validated_data['user'])
        response = {'token': token}
        return response

    def update(self, instance, validated_data):
        return instance

    def to_representation(self, instance):
        return instance


class WXAPhoneBindSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True, help_text='系统ID')
    phone = fields.CharField(required=True, write_only=True, help_text='手机号')
    phone_access = fields.CharField(required=True, write_only=True, help_text='验证码')
    appid = fields.CharField(required=False, allow_null=True, allow_blank=True, write_only=True, help_text='小程序APPID')
    code = fields.CharField(required=True, write_only=True, help_text='临时登录凭证code')
    token = fields.CharField(read_only=True, help_text='用户访问令牌')

    def validate(self, data):
        sys_id, phone, pa = data['sys_id'], data['phone'], data['phone_access']
        appid = data.get('appid', '')
        try:
            access = PhoneAccess.objects.get(phone=phone, phone_access=pa, sys_id=sys_id)
            if phone != '17704818161':
                access.delete()
        except PhoneAccess.DoesNotExist:
            raise ValidationError('验证码错误')
        try:
            user = User.objects.get(mobile=phone, sys_id=sys_id)
            if not user.is_active:
                msg = '该用户已停用'
                raise ValidationError(msg)
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        try:
            wechat_config = get_wechat_config(sys_id, wxa_aid=appid)  # type: WechatConfig
        except ValueError:
            raise ValidationError('微信小程序未配置')
        code = data['code']
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
        try:
            wx_data = wechat_client.wxa.code_to_session(code)
        except WeChatClientException:
            raise ValidationError('code已使用')
        users = User.objects.exclude(mobile=phone).filter(wxa_oid=wx_data['openid'])
        if users:
            raise ValidationError('其它用户已绑定此微信，请更换微信号后进行绑定')
        user.wxa_oid = wx_data['openid']
        user.save()
        return {'user': user}

    def create(self, validated_data):
        token = user_login(self.context['request'], validated_data['user'])
        response = {'token': token}
        return response

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class WXAUsernameBindSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True, help_text='系统ID')
    username = fields.CharField(required=True, write_only=True, help_text='用户名')
    password = fields.CharField(required=True, write_only=True, help_text='密码')
    appid = fields.CharField(required=False, allow_null=True, allow_blank=True, write_only=True, help_text='小程序APPID')
    code = fields.CharField(required=True, write_only=True, help_text='临时登录凭证code')
    token = fields.CharField(read_only=True, help_text='用户访问令牌')

    def validate(self, data):
        sys_id, username, password = data['sys_id'], data['username'], data['password']
        appid = data.get('appid', '')
        try:
            user = User.objects.get(username=username, sys_id=sys_id)
            if not user.is_active:
                msg = '该用户已停用'
                raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            raise ValidationError('用户名或密码错误')
        if not user.check_password(password):
            raise ValidationError('用户名或密码错误')
        try:
            wechat_config = get_wechat_config(sys_id, wxa_aid=appid)  # type: WechatConfig
        except ValueError:
            raise ValidationError('微信小程序未配置')
        code = data['code']
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
        try:
            wx_data = wechat_client.wxa.code_to_session(code)
        except WeChatClientException as e:
            logger.exception('微信错误: {}: {}'.format(sys_id, str(e)))
            raise ValidationError('code已使用')
        users = User.objects.exclude(username=username).filter(wxa_oid=wx_data['openid'])
        if users:
            raise ValidationError('其它用户已绑定此微信，请更换微信号后进行绑定')
        user.wxa_oid = wx_data['openid']
        user.save()
        return {'user': user}

    def create(self, validated_data):
        token = user_login(self.context['request'], validated_data['user'])
        response = {'token': token}
        return response

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class MPGetAuthURLSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, write_only=True, help_text='系统ID')
    uri = fields.CharField(write_only=True, help_text='微信授权成功后重定向地址')
    state = fields.CharField(required=False, allow_null=True, allow_blank=True,
                             write_only=True, help_text='其它状态保存,重定向后可从url query获取')
    authorize_url = fields.CharField(read_only=True, help_text='微信授权地址,获取后需直接在微信内打开此链接')

    def validate(self, data):
        sys_id, uri, state = data['sys_id'], data['uri'], data.get('state')
        try:
            wechat_config = get_wechat_config(sys_id)
        except ValueError:
            raise ValidationError('微信未配置')
        mp_aid = getattr(wechat_config, 'mp_aid')
        mp_sk = getattr(wechat_config, 'mp_sk')
        if not mp_aid or not mp_sk:
            raise ValidationError('微信公众号未配置')
        try:
            wx_data = WeChatOAuth(mp_aid, mp_sk, uri, state=state)
            authorize_url = wx_data.authorize_url
        except WeChatOAuthException:
            raise ValidationError('微信授权失败')
        data = {'authorize_url': authorize_url}
        return data

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class MPCodeToOpenIDSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, help_text='系统ID')
    uri = fields.CharField(write_only=True, help_text='微信授权成功后重定向地址')
    code = fields.CharField(write_only=True, help_text='重定向后返回的code')
    open_id = fields.CharField(read_only=True, help_text='返回OpenID')

    def validate(self, data):
        sys_id, code, uri = data['sys_id'], data['code'], data['uri']
        try:
            wechat_config = get_wechat_config(sys_id)
        except ValueError:
            raise ValidationError('微信未配置')
        mp_aid = getattr(wechat_config, 'mp_aid')
        mp_sk = getattr(wechat_config, 'mp_sk')
        if not mp_aid or not mp_sk:
            raise ValidationError('微信公众号未配置')
        try:
            open_id = WeChatOAuth(mp_aid, mp_sk, uri).fetch_access_token(code)['openid']
        except WeChatOAuthException:
            raise ValidationError('微信授权失败')
        data = {'open_id': open_id}
        return data

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class MPOpenIDAuthenticationSerializer(serializers.Serializer):
    sys_id = fields.IntegerField(help_text='sys_id', write_only=True, required=True)
    openid = fields.CharField(required=True, write_only=True, help_text='OpenID')
    token = fields.CharField(read_only=True, help_text='token')

    def validate(self, data):
        sys_id, openid = data['sys_id'], data['openid']
        try:
            user = User.objects.filter(sys_id=sys_id).get(wechart_oid=openid)
            if not user.is_active:
                msg = '该用户已停用'
                raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            raise ValidationError('用户不存在')
        return {'user': user}

    def create(self, validated_data):
        token = user_login(self.context['request'], validated_data['user'])
        data = {'token': token}
        return data

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


class MPOpenIDNamePhoneBindSerializer(serializers.Serializer):
    sys_id = fields.IntegerField(help_text='sys_id', write_only=True, required=True)
    openid = fields.CharField(required=True, write_only=True, help_text='OpenID')
    name = fields.CharField(required=True, write_only=True, help_text='姓名')
    phone = fields.CharField(required=True, write_only=True, help_text='手机号')
    msg = fields.CharField(read_only=True, help_text='成功提示')

    def validate(self, data):
        sys_id, name, phone = data['sys_id'], data['name'], data['phone']
        users = User.objects.filter(sys_id=sys_id, full_name=name, mobile=phone)
        user_count = users.count()
        if user_count > 1 or user_count == 0:
            raise ValidationError('用户不存在')
        user = users[0]
        if user.wechart_oid:
            raise ValidationError('用户已绑定')
        return {'user': user, 'openid': data['openid']}

    def create(self, validated_data):
        user = validated_data['user']
        openid = validated_data['openid']
        user.wechart_oid = openid
        user.save()
        return {'msg': '绑定成功'}

    def update(self, instance, validated_data):
        return self.create(validated_data)


class MPCodeAuthenticationSerializer(serializers.Serializer):
    sys_id = fields.IntegerField(help_text='sys_id', required=True)
    org_id = fields.IntegerField(help_text='org_id', default=1, required=False)
    code = fields.CharField(required=True, help_text='Code')
    token = fields.CharField(read_only=True, help_text='token')
    mobile = fields.CharField(read_only=True, help_text='手机号')
    full_name = fields.CharField(read_only=True, help_text='姓名')
    uid = fields.CharField(read_only=True, help_text='UID')

    def validate(self, data):
        sys_id, org_id, code = data['sys_id'], data['org_id'], data['code']
        try:
            wechat_config = get_wechat_config(sys_id)
        except ValueError:
            raise ValidationError('微信未配置')
        mp_aid = getattr(wechat_config, 'mp_aid')
        mp_sk = getattr(wechat_config, 'mp_sk')
        if not mp_aid or not mp_sk:
            raise ValidationError('微信公众号未配置')
        try:
            open_id = WeChatOAuth(mp_aid, mp_sk, 'localhost').fetch_access_token(code)['openid']
        except WeChatOAuthException:
            raise ValidationError('微信授权失败')
        try:
            user = User.objects.filter(sys_id=sys_id).get(wechart_oid=open_id)
            if not data['user'].is_active:
                msg = '该用户已停用'
                raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            username = next_username(sys_id)
            user = User.objects.create_user(
                useername=username, password=str(time.time()),
                full_name=username,
                sys_id=sys_id, org_id=org_id, wechart_oid=open_id
            )
            user.save()
        return {'user': user}

    def create(self, validated_data):
        user = validated_data['user']  # type: User
        token = user_login(self.context['request'], validated_data['user'])
        response = {
            'token': token, 'openid': user.wechart_oid, 'mobile': user.mobile,
            'full_name': user.full_name, 'uid': user.pk
        }
        return response

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def to_representation(self, instance):
        return instance


def qrid_raw(plain_str: str) -> str:
    return f'QR-{plain_str}'


def qrid_plain(raw_str: str) -> str:
    return raw_str[3:]


class QRLoginGetCodeSerializer(serializers.Serializer):
    code = serializers.CharField(read_only=True, help_text='授权令牌CODE')

    def create(self, validated_data):
        code_plain = str(uuid.uuid4())
        code_raw = qrid_raw(code_plain)
        data = {'status': 'wait', 'token': ''}
        conn = get_redis_connection("default")  # type: redis.Redis
        conn.setex(code_raw, QR_LOGIN_EXP_TIME_SEC, json.dumps(data))
        return {'code': code_plain}

    def update(self, instance, validated_data):
        return instance


class QRLoginCheckLoginSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True, help_text='授权令牌CODE')
    status = serializers.CharField(
        read_only=True, help_text='令牌状态：["timeout", "wait", "login"], 代表过期、未登录、已登录')
    token = serializers.CharField(
        read_only=True, help_text='登录后的身份令牌token'
    )

    def create(self, validated_data):
        code_plain = validated_data['code']
        code_raw = qrid_raw(code_plain)
        conn = get_redis_connection("default")  # type: redis.Redis
        data = conn.get(code_raw)
        if data is None:
            return {'status': 'timeout', 'token': ''}
        return json.loads(data)

    def update(self, instance, validated_data):
        pass


class QRLoginAuthSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True, help_text='授权令牌CODE')
    status = serializers.CharField(
        read_only=True, help_text='令牌状态：["timmeout", "login"], 代表过期、已登录')

    def create(self, validated_data):
        code_plain = validated_data['code']
        try:
            user = self.context['request'].user
        except (AttributeError, KeyError) as e:
            logger.exception('找不到用户')
            return {'status': 'timeout'}

        if not user.is_active:
            msg = '该用户已停用'
            return {'status': 'timeout', 'msg': msg}
        code_raw = qrid_raw(code_plain)
        conn = get_redis_connection("default")  # type: redis.Redis
        data = conn.get(code_raw)
        if data is None:
            return {'status': 'timeout'}
        user_logged_in.send(sender=user.__class__, request=self.context['request'], user=user)
        data = json.loads(data)
        data['status'] = 'login'
        data['token'] = user_login(self.context['request'], user)
        conn.setex(code_raw, QR_LOGIN_EXP_TIME_SEC, json.dumps(data))
        return {'status': data['status']}

    def update(self, instance, validated_data):
        pass
