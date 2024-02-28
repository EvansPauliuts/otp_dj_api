# from core.conf.boilerplate import BASE_DIR
from core.conf.environ import env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    },
}

if not env('DEBUG'):
    DATABASES['default']['CONN_MAX_AGE'] = 600
