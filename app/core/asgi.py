"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
from decouple import config
from django.core.asgi import get_asgi_application

environment = config('ENVIRONMENT')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'core.settings.{environment}')

application = get_asgi_application()
