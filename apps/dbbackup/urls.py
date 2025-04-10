from django.urls import path
from . import api

urlpatterns = (
    path('api/v1/dbbackup/', api.DBBackupAPI.as_view()),
    path('api/v1/dbrestore/', api.DBRestoreAPI.as_view()),
)
