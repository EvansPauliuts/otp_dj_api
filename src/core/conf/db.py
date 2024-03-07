from core.conf.environ import env
from core.conf.boilerplate import BASE_DIR

if env('DB_USE_DOCKER', cast=int):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
            'OPTIONS': {
                'options': '-c statement_timeout=60000',
                'server_side_binding': True,
                'connect_timeout': 10,
                'client_encoding': 'UTF8',
                'sslmode': env('DB_SSL_MODE', cast=str, default=''),
            },
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

if not env('DEBUG'):
    DATABASES['default']['CONN_MAX_AGE'] = 600
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = False
