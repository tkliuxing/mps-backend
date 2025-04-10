from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView


urlpatterns = [
    path('', include('baseconfig.urls')),
    path('', include('usercenter.urls')),
    path('', include('utility.urls')),
    path('', include('notice.urls')),
    path('', include('gps.urls')),
    path('', include('social.urls')),
    path('', include('formtemplate.urls')),
    path('', include('article.urls')),
    path('', include('system.urls')),
    path('', include('parameter.urls')),
    path('', include('account.urls')),
    path('', include('dbbackup.urls')),
    path('myadminmy/', admin.site.urls),
    re_path(r'^ueditor/', include('DjangoUeditor.urls')),
    path('api/v1/captcha/', include('rest_captcha.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.urls import re_path as url
    from rest_framework.permissions import IsAuthenticatedOrReadOnly
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    schema_view = get_schema_view(
        openapi.Info(
            title="API",
            default_version='v1',
            description="API接口文档",
            contact=openapi.Contact(email="xxx@xx.com"),
        ),
        patterns=[
            path('', include('baseconfig.urls')),
            path('', include('usercenter.urls')),
            path('', include('utility.urls')),
            path('', include('notice.urls')),
            path('', include('gps.urls')),
            path('', include('social.urls')),
            path('', include('formtemplate.urls')),
            path('', include('article.urls')),
            path('', include('system.urls')),
            path('', include('parameter.urls')),
            path('', include('account.urls')),
            path('', include('dbbackup.urls')),
        ],
        public=True,
        permission_classes=(IsAuthenticatedOrReadOnly,),
    )
    urlpatterns += [
        url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=60), name='schema-json'),
        url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=60), name='schema-swagger-ui'),
        url(r'^api-docs/$', schema_view.with_ui('redoc', cache_timeout=60), name='schema-redoc'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

