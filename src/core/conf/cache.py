from core.conf.environ import env

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_BROKER_URL = env('RABBITMQ_URL')
FLOWER_BASIC_AUTH = env('FLOWER_BASIC_AUTH')

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
