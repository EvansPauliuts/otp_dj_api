import dotenv

from core.conf.boilerplate import BASE_DIR

env_path = BASE_DIR / '.env'

config = dotenv.load_dotenv(dotenv_path=env_path)

if env_path.exists():
    dotenv.load_dotenv(
        dotenv_path=env_path,
    )

__all__ = [
    config,
]
