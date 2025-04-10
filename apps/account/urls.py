from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api


router = DefaultRouter()

router.register(r'account', api.AccountViewSet)
router.register(r'account-myaccount', api.MyAccountView)
router.register(r'account-create', api.AccountCreateView)
router.register(r'account-statements', api.AccountStatementsViewSet)

urlpatterns = (
    path('api/v1/', include(router.urls)),
)
