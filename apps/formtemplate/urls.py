from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api


router = DefaultRouter()

router.register(r'formfields', api.FormFieldsViewSet)
router.register(r'formtemplate', api.FormTemplateViewSet)
router.register(r'formtemplatemin', api.FormTemplateMinViewSet)
router.register(r'formtemplatecode', api.FormTemplateCodeViewSet)
router.register(r'formaggrgatefields', api.FormAggrgateFieldsViewSet)
router.register(r'reportconf', api.FormDataReportConfViewSet)
router.register(r'formtemplatecopy', api.FormTemplateCopyViewSet)
router.register(r'data', api.DataViewSet)
router.register(r'datafind', api.DataFindViewSet)
router.register(r'data-delete', api.DataBulkDeleteView)
router.register(r'data-update', api.DataBulkUpdateView)
router.register(r'data-field-list', api.DataFieldViewSet)
router.register(r'data-aggregate', api.DataAggregateViewSet)

urlpatterns = (
    path('api/v1/', include(router.urls)),
    path('api/v1/data-delete-one/', api.data_delete_one),
    path('api/v1/formdatareport/<int:report_id>/', api.FormDataReportView.as_view()),
    path('api/v1/reportcomp/<int:report_id>/', api.FormDataReportCompressionView.as_view()),
    path('api/v1/testreport/', api.FormDataReportTestView.as_view()),
)
