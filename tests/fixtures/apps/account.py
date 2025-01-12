import uuid

import pytest
from rest_framework.test import APIClient

from tests.factories.apps.accounts import BusinessUnitFactory
from tests.factories.apps.accounts import JobTitleFactory
from tests.factories.apps.accounts import OrganizationFactory
from tests.factories.apps.accounts import ProfileFactory
from tests.factories.apps.accounts import TokenFactory
from tests.factories.apps.accounts import UserFactory


def api_client_with_credentials(token, api_client):
    return api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


@pytest.fixture
def token():
    yield TokenFactory()


@pytest.fixture
def business_unit():
    yield BusinessUnitFactory()


@pytest.fixture
def organization():
    yield OrganizationFactory()


@pytest.fixture
def user():
    yield UserFactory()


@pytest.fixture
def user_multiple():
    yield UserFactory.create_batch(10)


@pytest.fixture
def user_profile():
    yield ProfileFactory()


@pytest.fixture
def api_client(token):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {token.key}',
        HTTP_X_IDEMPOTENCY_KEY=str(uuid.uuid4()),
    )
    yield client


@pytest.fixture
def unauthenticated_api_client():
    yield APIClient()


@pytest.fixture
def job_title():
    yield JobTitleFactory()


@pytest.fixture
def user_api(api_client, organization, business_unit):
    job_title = JobTitleFactory()

    yield api_client.post(
        '/api/v1/users/',
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
