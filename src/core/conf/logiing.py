LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'rich': {
            'datefmt': '[%X]',
        },
    },
    'handlers': {
        'console': {
            'class': 'rich.logging.RichHandler',
            'filters': ['require_debug_true'],
            'formatter': 'rich',
            'level': 'DEBUG',
            'rich_tracebacks': True,
            'tracebacks_show_locals': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': [],
            'level': 'INFO',
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
