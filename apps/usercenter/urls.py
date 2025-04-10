from django.urls import path, include
from rest_framework import routers
from django.views.generic.base import RedirectView

from . import api
from . import auth

router = routers.DefaultRouter()
router.register(r'user', api.UserViewSet)
router.register(r'usermin', api.UserMinViewSet)
router.register(r'userfind', api.UserFindAPI)
router.register(r'group', api.GroupViewSet)
router.register(r'permissions', api.PermissionViewSet)
router.register(r'permissionstree', api.PermissionTreeViewSet)
router.register(r'department', api.TreeDepartmentViewSet)
router.register(r'flatdepartment', api.DepartmentViewSet)
router.register(r'departmentmove', api.DepartmentMoveView)
router.register(r'changepwd', api.ChangePasswordApi)
router.register(r'myinfo', api.MyInfoViewSet)
router.register(r'userphonereg', api.UserPhoneRegView)
router.register(r'userreg', api.UserCaptchaRegView)
router.register(r'orguserreg', api.OrgUserCaptchaRegView)
router.register(r'userphonecheck', api.UserPhoneCheck)
router.register(r'departmenttxl', api.TxlViewSet)

router.register(r'smscode', auth.PhoneAccessViewSet)
router.register(r'phonelogin', auth.PhoneLoginViewSet)
router.register(r'phoneaccessvalidate', auth.PhoneAccessValidateViewSet)

router.register(r'emailaccess', auth.EmailAccessViewSet)
router.register(r'emailaccessvalidate', auth.EmailAccessValidateViewSet)
router.register(r'emaillogin', auth.EmailLoginViewSet)

router.register(r'wxa-reglogin', auth.WXARegLoginViewSet)
router.register(r'wxa-login', auth.WXALoginViewSet)
router.register(r'wxa-phonebind', auth.WXAPhoneBindViewSet)
router.register(r'wxa-userbind', auth.WXAUsernameBindViewSet)

router.register(r'mp-getauthurl', auth.MPGetAuthURLView)
router.register(r'mp-codetoopenid', auth.MPCodeToOpenIDView)
router.register(r'mp-openidlogin', auth.MPOpenIDLoginViewSet)
router.register(r'mp-codereglogin', auth.MPCodeLoginRegViewSet)
router.register(r'mp-openidnamephonebind', auth.MPOpenIDNamePhoneBindViewSet)

router.register(r'qrlogin-getcode', auth.QRLoginGetCodeViewSet)
router.register(r'qrlogin-checklogin', auth.QRLoginCheckLoginViewSet)
router.register(r'qrlogin-auth', auth.QRLoginAuthViewSet)

urlpatterns = (
    # path('', RedirectView.as_view(url='/pm/')),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', auth.obtain_jwt_token),
    path('api/v1/authlogin/', auth.CaptchaLoginViewSet.as_view()),
)
