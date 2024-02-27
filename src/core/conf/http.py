from core.conf.environ import env

ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')
CORS_ALLOW_ALL_ORIGINS = True
