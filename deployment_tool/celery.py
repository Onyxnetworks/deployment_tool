import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deployment_tool.settings')

app = Celery('deployment_tool')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
