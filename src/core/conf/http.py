from core.conf.environ import config

ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')
CORS_ALLOW_ALL_ORIGINS = True
