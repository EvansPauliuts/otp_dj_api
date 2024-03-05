import pytest
from django.core.cache import cache

from tests.factories.apps.accounts import JobTitleFactory

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


@pytest.fixture
def job_title():
    yield JobTitleFactory()


@pytest.fixture
def user_api(api_client, organization, business_unit):
    job_title = JobTitleFactory()
    yield api_client.post(
        '/api/users/',
        {
            'organization': organization.id,
            'business_unit': business_unit.id,
            'username': 'foobar',
            'email': 'test@test.com',
            'profile': {
                'business_unit': business_unit.id,
                'organization': organization.id,
                'first_name': 'foo',
                'last_name': 'bar',
                'address_line_1': 'test address line 1',
                'city': 'test',
                'state': 'NC',
                'zip_code': '12345',
                'job_title': job_title.id,
            },
        },
        format='json',
    )
