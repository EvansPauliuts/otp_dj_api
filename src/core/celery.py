import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

from core.conf.environ import env

__all__ = [
    'celery',
]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

celery = Celery('app')

celery.conf.update(
    broker_url=env('CELERY_BROKER_URL'),
    task_always_eager=env('CELERY_ALWAYS_EAGER', cast=bool, default=settings.DEBUG),
    task_eager_propagates=True,
    task_ignore_result=True,
    task_store_errors_even_if_ignored=True,
    task_acks_late=True,
    timezone=env('TIME_ZONE', cast=str, default='Europe/Moscow'),
    beat_schedule={
        'delete-old-activation-codes': {
            'task': 'apps.tasks.delete_old_activation_codes',
            'schedule': crontab(minute='*/2'),
        },
    },
)

celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@celery.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
