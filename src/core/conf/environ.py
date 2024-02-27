import dotenv

from core.conf.boilerplate import BASE_DIR

env_path = BASE_DIR / '.env'
env = dotenv.load_dotenv(
    dotenv_path=env_path,
)

__all__ = [
    env,
]
