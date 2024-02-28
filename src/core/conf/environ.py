import os

import dotenv

from core.conf.boilerplate import BASE_DIR

env_path = BASE_DIR / '.env'

if env_path.exists():
    dotenv.load_dotenv(
        dotenv_path=env_path,
    )

env = os.getenv

__all__ = [
    env,
]
