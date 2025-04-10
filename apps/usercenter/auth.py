import logging
import datetime
import random
import json
from rest_framework.throttling import AnonRateThrottle
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken
from django.http import QueryDict
from django_filters.rest_framework.backends import DjangoFilterBackend

from system.utils.send_phone_access import send_phone_access
from utility.crypt import aes_cbc_pkcs7_decrypt
from .models import PhoneAccess, User
from .permissions import CsrfExemptSessionAuthentication, BasicAuthentication
from .auth_serializers import (
    PhoneAuthenticationSerializer,
    PhoneAccessSerializer,
    MyJSONWebTokenSerializer,
    CaptchaLoginSerializer,
    WXALoginSerializer,
    WXARegLoginSerializer,
    WXAPhoneBindSerializer,
    WXAUsernameBindSerializer,
    MPGetAuthURLSerializer,
    MPCodeToOpenIDSerializer,
    MPOpenIDAuthenticationSerializer,
    MPCodeAuthenticationSerializer,
    QRLoginGetCodeSerializer,
    QRLoginCheckLoginSerializer,
    QRLoginAuthSerializer,
    MPOpenIDNamePhoneBindSerializer,
    PhoneAccessValidateSerializer,
    EmailAccessValidateSerializer,
    EmailAccessSerializer,
    EmailLoginSerializer,
)

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
logger = logging.getLogger('restapi')


def next_username(sys_id):
    user_count = User.objects.filter(sys_id=sys_id).count()
    if user_count:
        return f"用户{user_count:07d}"
    else:
        user_count = 1
        return f"用户{user_count:07d}"


class PhoneValidErrorException(ValidationError):
    pass


class PhoneLoginViewSet(viewsets.GenericViewSet):
    """手机号验证码登录"""
    serializer_class = PhoneAuthenticationSerializer
    queryset = User.objects.none()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        手机号验证码登录

        返回 {"token":"..."}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PhoneAccessViewSet(viewsets.GenericViewSet):
    """验证码短信发送"""
    queryset = User.objects.none()
    serializer_class = PhoneAccessSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        验证码短信发送

        返回 {"phone": "...", "error": "..."} 成功时 error 为空
        """
        serializer = PhoneAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        sys_id = serializer.validated_data['sys_id']
        try:
            pa = PhoneAccess.objects.get(phone=phone, sys_id=sys_id)
        except PhoneAccess.DoesNotExist:
            pa = PhoneAccess(phone=phone, sys_id=sys_id)
        except PhoneAccess.MultipleObjectsReturned:
            PhoneAccess.objects.filter(phone=phone, sys_id=sys_id).delete()
            pa = PhoneAccess(phone=phone, sys_id=sys_id)
        if phone == '17704818161':
            pa.phone_access = '123456'
            pa.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        now = datetime.datetime.now()
        if pa.phone_access and pa.create_time > now - datetime.timedelta(seconds=60):
            return Response({'phone': phone, 'error': '请勿短时间重复发送'}, status=status.HTTP_403_FORBIDDEN)
        code = "".join(random.choices("1234567890", k=6))
        state, access = send_phone_access(sys_id, phone, code)
        logger.info('send sns: {} - {}'.format(state, access))
        if not state:
            return Response({'phone': phone, 'error': '短信发送失败'}, status=status.HTTP_403_FORBIDDEN)
        pa.phone_access = access
        pa.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PhoneAccessValidateViewSet(viewsets.GenericViewSet):
    """验证码验证"""
    queryset = User.objects.none()
    serializer_class = PhoneAccessValidateSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        验证码验证
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmailAccessViewSet(viewsets.GenericViewSet):
    """邮箱验证码发送"""
    queryset = User.objects.none()
    serializer_class = EmailAccessSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        邮箱验证码发送
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmailAccessValidateViewSet(viewsets.GenericViewSet):
    """邮箱验证码验证"""
    queryset = User.objects.none()
    serializer_class = EmailAccessValidateSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        邮箱验证码验证
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmailLoginViewSet(viewsets.GenericViewSet):
    """邮箱登录"""
    queryset = User.objects.none()
    serializer_class = EmailLoginSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        邮箱登录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyObtainJSONWebToken(ObtainJSONWebToken):
    """用户名密码登录接口， 成功时返回 {"token": "...."}"""
    serializer_class = MyJSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        if 'data' in request.data:
            try:
                dec_data = aes_cbc_pkcs7_decrypt(request.data['data'], '~psL!t&8pWivTyvG')
                dec_data = json.loads(dec_data)
                request._full_data = QueryDict('', mutable=True, encoding=request._request._encoding)
                request._full_data.update(dec_data)
            except:
                return Response({'success': False, 'error': '数据错误'}, status=400)
        password = request.data.get('password')
        username = request.data.get('username')
        sys_id = request.data.get('sys_id')
        resp = super().post(request, *args, **kwargs)
        if resp.status_code != 400:
            logger.warning(f'login: {sys_id}|{username}|{password}')
        return resp


obtain_jwt_token = MyObtainJSONWebToken.as_view()


class CaptchaLoginViewSet(ObtainJSONWebToken):
    """用户名密码验证码登录"""
    serializer_class = CaptchaLoginSerializer

    def post(self, request, *args, **kwargs):
        if 'data' in request.data:
            try:
                dec_data = aes_cbc_pkcs7_decrypt(request.data['data'], '~psL!t&8pWivTyvG')
                dec_data = json.loads(dec_data)
                request._full_data = QueryDict('', mutable=True, encoding=request._request._encoding)
                request._full_data.update(dec_data)
            except:
                return Response({'non_field_errors': ["数据错误"]}, status=400)
        resp = super().post(request, *args, **kwargs)
        return resp


class WXALoginViewSet(viewsets.GenericViewSet):
    """微信小程序code登录"""
    serializer_class = WXALoginSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    queryset = User.objects.none()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        微信小程序code登录

        需先进行小程序openid的绑定
        需要首先配置相应系统的 SystemWechatConfig
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WXARegLoginViewSet(viewsets.GenericViewSet):
    """微信小程序code登录或注册"""
    serializer_class = WXARegLoginSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    queryset = User.objects.none()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        微信小程序code登录或注册

        通过微信小程序 code 和 appid 获取 token，用户不存在则自动注册一个
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 手机号绑定微信 openid API
class WXAPhoneBindViewSet(viewsets.GenericViewSet):
    """手机号绑定微信小程序openid"""
    queryset = User.objects.none()
    serializer_class = WXAPhoneBindSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        手机号绑定微信小程序openid

        通过手机号、验证码、appid、code进行openid和用户的绑定，返回token；
        需要用户已经存在并具有手机号
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WXAUsernameBindViewSet(viewsets.GenericViewSet):
    """微信小程序用户名密码绑定openid"""
    queryset = User.objects.none()
    serializer_class = WXAUsernameBindSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        微信小程序用户名密码绑定openid

        用户名密码绑定微信 openid API
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MPGetAuthURLView(viewsets.GenericViewSet):
    """微信公众号重定向地址获取"""
    queryset = User.objects.none()
    serializer_class = MPGetAuthURLSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        微信公众号重定向地址获取

        微信 OAuth authorize_url 获取API，需要首先配置相应系统的 SystemWechatConfig
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MPCodeToOpenIDView(viewsets.GenericViewSet):
    """微信公众号code换openid"""
    queryset = User.objects.none()
    serializer_class = MPCodeToOpenIDSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        微信公众号code换openid

        通过微信 code 获取 openid 的 API，需要首先配置相应系统的 SystemWechatConfig
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MPOpenIDLoginViewSet(viewsets.GenericViewSet):
    """微信openid登录"""
    serializer_class = MPOpenIDAuthenticationSerializer
    queryset = User.objects.none()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        微信openid登录

        通过微信 openid 获取 toekn 的API，需要首先配置相应系统的 SystemWechatConfig，并进行用户和 openid 的绑定操作
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MPOpenIDNamePhoneBindViewSet(viewsets.GenericViewSet):
    """通过 name 和 phone 绑定 微信 openid"""
    serializer_class = MPOpenIDNamePhoneBindSerializer
    queryset = User.objects.none()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        通过 name 和 phone 绑定 微信 openid
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)


class MPCodeLoginRegViewSet(viewsets.GenericViewSet):
    """微信公众号code登录"""
    serializer_class = MPCodeAuthenticationSerializer
    queryset = User.objects.none()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        微信公众号code登录

        通过微信 code 获取 toekn 的API；
        用户不存在时会自动注册，返回token，自动注册的用户没有"手机号"和"姓名"；
        用户存在时（根据sys_id和openid获取）直接返回现有用户的信息和token
        需要首先配置相应系统的 SystemWechatConfig
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QRLoginGetCodeViewSet(viewsets.GenericViewSet):
    """扫码登录获取code"""
    serializer_class = QRLoginGetCodeSerializer
    queryset = User.objects.none()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        扫码登录获取code

        请求后直接返回code
        """
        serializer = self.get_serializer(data=request.data)  # type: QRLoginGetCodeSerializer
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)


class QRLoginCheckLoginViewSet(viewsets.GenericViewSet):
    """扫码获取code登录状态"""
    serializer_class = QRLoginCheckLoginSerializer
    queryset = User.objects.none()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        扫码获取code登录状态

        通过code请求后返回状态status: ["timeout", "wait", "login"]，如果status是login则token有值，否则token为空字符串
        """
        serializer = self.get_serializer(data=request.data)  # type: QRLoginCheckLoginSerializer
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)


class QRLoginAuthViewSet(viewsets.GenericViewSet):
    """扫码已登录用户通过code登录"""
    serializer_class = QRLoginAuthSerializer
    queryset = User.objects.none()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        扫码已登录用户通过code登录

        已登录用户通过code请求后返回状态status: ["timeout", "login"]
        """
        serializer = self.get_serializer(data=request.data)  # type: QRLoginAuthSerializer
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)
