import environ

from core.conf.boilerplate import BASE_DIR

env = environ.Env(
    DEBUG=(bool, False),
    CI=(bool, False),
)

env_path = BASE_DIR / '.env'

if env_path.exists():
    env.read_env(env_path)


__all__ = [
    'env',
]
