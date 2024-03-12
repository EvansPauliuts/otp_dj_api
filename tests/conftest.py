import pytest
from django.core.cache import cache

pytest_plugins = [
    'tests.factories.apps.accounts',
    'tests.factories.apps.location',
    'tests.fixtures.apps.account',
    'tests.fixtures.apps.location',
]


@pytest.fixture(autouse=True)
def _cache(request):
    yield
    cache.clear()
