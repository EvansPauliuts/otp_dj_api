import os

from celery import Celery
from django.conf import settings

from core.conf.environ import env

__all__ = [
    'celery',
]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

celery = Celery('app')

celery.conf.update(
    broker_url=env('CELERY_BROKER_URL'),
    beat_schedule={},
)

celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@celery.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
