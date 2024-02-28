import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

from core.conf.environ import env

__all__ = [
    'celery',
]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

celery = Celery('app')

celery.conf.update(
    broker_url=env('CELERY_BROKER_URL'),
    beat_schedule={
        'delete-old-activation-codes': {
            'task': 'apps.tasks.delete_old_activation_codes',
            'schedule': crontab(minute='*/2'),
        }
    },
)

celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@celery.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
