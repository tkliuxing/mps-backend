from django.urls import path, include
from rest_framework import routers

from . import api

router = routers.DefaultRouter()
router.register(r'utils-pinyin', api.PinYinViewSet)
router.register(r'utils-wechatjssign', api.WechatJsSign)
router.register(r'utils-wechatappphonenum', api.WechatAppPhoneNum)
router.register(r'utils-wechatappqrcode', api.WechatAppQrCode)
router.register(r'mp-send-template-msg', api.MPTemplateMsgSendAPI)
router.register(r'wxa-send-template-msg', api.WXATemplateMsgSendAPI)
router.register(r'utils-smssendcode', api.SMSSendCodeAPI)
router.register(r'utils-smsvalidcode', api.SMSCodeValidAPI)


urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
    path('api/v1/exportword/', api.exportword),
    path('api/v1/exportsvg/', api.exportsvg),
    path('api/v1/docx_to_pdf/', api.docx_to_pdf),
    path('api/v1/save_sign_pdf/', api.save_sign_pdf),
    path('api/v1/add_image_to_pdf/', api.add_image_to_pdf_api),
)
