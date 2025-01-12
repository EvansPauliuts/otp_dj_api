from core.conf.environ import env

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_BROKER_URL = env('CELERY_BROKER_URL', cast=str)
FLOWER_BASIC_AUTH = env('FLOWER_BASIC_AUTH', cast=str)

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


if env('DB_USE_DOCKER', cast=bool):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': env('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
        },
        'sessions': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': env('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PREFIX': 'sessions',
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 100,
                    'retry_on_timeout': True,
                },
            },
        },
        'celery': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': env('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PREFIX': 'celery',
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 100,
                    'retry_on_timeout': True,
                },
            },
        },
        'idempotency': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': env('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
        },
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
    }
