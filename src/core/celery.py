import os

from celery import Celery
from django.apps import AppConfig
from django.apps import apps
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

APP = Celery('core')


class CeleryConfig(AppConfig):
    name = 'core'
    verbose_name = 'Celery Config'

    def ready(self):
        APP.config_from_object('django.conf:settings', namespace='CELERY')
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        APP.autodiscover_tasks(installed_apps, force=True)

    def tearDown(self):
        pass
