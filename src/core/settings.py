from split_settings.tools import include

from core.conf.environ import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG')


include(
    'conf/api.py',
    'conf/auth.py',
    'conf/boilerplate.py',
    'conf/cache.py',
    'conf/db.py',
    'conf/debug_toolbar.py',
    'conf/features.py',
    'conf/healthchecks.py',
    'conf/http.py',
    'conf/i18n.py',
    'conf/installed_apps.py',
    'conf/media.py',
    'conf/middleware.py',
    'conf/storage.py',
    'conf/static.py',
    'conf/templates.py',
    'conf/timezone.py',
    'conf/logging.py',
    'conf/versions.py',
)
