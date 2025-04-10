"""
暴露的env有：
DEBUG:  False or True
SECRET_KEY: 加密加盐传
DB_NAME: 数据库名
DB_USER: 数据库用户名
DB_PASSWORD: 数据库密码
DB_HOST: 数据库主机ip或域名
DB_PORT: 数据库端口
REDIS_URL: redis url 联接地址，不加bucket号
HOME: 当前用户 home 目录，不加最后的 '/'
STATIC_ROOT: 静态文件路径，需要能被nginx等访问到
MEDIA_ROOT: 上传文件路径，需要能被nginx等访问到，并且程序有权限写入
"""
import sys
import os
from corsheaders.defaults import default_headers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps/'))

SECRET_KEY = 'django-insecure-=*pf9vvt_wgj&bk1!#5wdt!11i2zb1b4i1lg%-t=*1hi3dgrpm'
_secret_key = os.getenv('SECRET_KEY')
if _secret_key is not None:
    SECRET_KEY = _secret_key

DEBUG = os.getenv('DEBUG', 'False') == 'True'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'dbbackup',
    'django_celery_results',
    'django_celery_beat',
    'rest_captcha',
    'drf_yasg',
    'django_filters',
    'mptt',
    'django_mptt_admin',

    # In apps folder app
    'DjangoUeditor',
    'usercenter',
    'baseconfig',
    'utility',
    'account',
    'notice',
    'gps',
    'formtemplate',
    'article',
    'customer',
    'org',
    'goods',
    'service',
    'system',
    'parameter',
    'social',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'mainbackend'),
        'USER': os.getenv('DB_USER', 'mainbackend'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'tyhbvfg56'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, 'backups/')}
DBBACKUP_CONNECTOR_MAPPING = {
    'django.db.backends.postgresql': 'dbbackup.db.postgresql.PgDumpConnector',
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_USER_MODEL = 'usercenter.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = ['usercenter.backend.UserAuthBackend']

SILENCED_SYSTEM_CHECKS = ["auth.W004"]

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

MEDIA_URL = '/media/'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'usercenter.pagination.UCPageNumberPagination',
    'PAGE_SIZE': 15,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'usercenter.authentication.MyJSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10000/day',
        'user': '1000000/day'
    }
}

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_VERIFY_EXPIRATION': False,
}

REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL + '1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL + '2',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

ASGI_APPLICATION = "project.asgi.application"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db': {
            'handlers': ['console'],
            'level': 'INFO',  # change to DEBUG to view console log
            'propagate': True,
        },
        'restapi': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'githook': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_URL = REDIS_URL + '2'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = (
    *default_headers,
    "X_requested_with",
)

CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True

ALLOWED_HOSTS = ['*']

STATIC_URL = '/static/'
STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'static/'))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(BASE_DIR, 'media/'))


try:
    from .local_settings import *
except ImportError:
    raise ImportError('please create local_settings.py file')
