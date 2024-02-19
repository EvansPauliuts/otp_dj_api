from .base import *
from ..log_filters import ManagementFilter

ALLOWED_HOSTS = ['*']

VERBOSE = '[%(asctime)s]%(levelname)s' ' [%(name)s]:%(lineno)s] %(message)s'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'remove_migration_sql': {
            '()': ManagementFilter,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['remove_migration_sql'],
            'class': 'logging.StreamHandler',
        },
    },
    'formatters': {
        'verbose': {
            'format': VERBOSE,
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
