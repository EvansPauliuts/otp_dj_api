from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'
