import os
from celery import Celery

__ALL__ = [
    'celery_app',
    '__version__',
]
__version__ = '2.0.0'


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
celery_app = app
