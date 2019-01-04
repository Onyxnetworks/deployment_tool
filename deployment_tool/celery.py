from __future__ import absolute_import

import os
from django.conf import settings
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deployment_tool.settings')

app = Celery('deployment_tool')
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.humanize(with_defaults=False, censored=True)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
