import pytest
from django.core.cache import cache

pytest_plugins = [
    'tests.factories.apps.users',
    'tests.fixtures.apps.users',
]


def api_client_with_credentials(token, api_client):
    return api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


@pytest.fixture(autouse=True)
def _cache(request):
    yield
    cache.clear()
