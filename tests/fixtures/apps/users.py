import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from tests.factories.apps.users import UserFactory, TokenFactory

register(UserFactory)
register(TokenFactory)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def active_user(db, user_factory):
    return user_factory.create(is_active=True)


@pytest.fixture
def inactive_user(db, user_factory, user):
    return user_factory.create(is_active=False)


@pytest.fixture
def auth_user_password():
    return 'hello@@@111'


@pytest.fixture
def authenticate_user(
    api_client,
    active_user,
    auth_user_password,
):
    def _user(
        verified=True,
        is_active=True,
        is_admin=False,
    ):
        active_user.verified = verified
        active_user.is_active = is_active
        active_user.is_admin = is_admin
        active_user.save()
        active_user.refresh_from_db()

        url = reverse('users:login')

        data = {
            'phone': active_user.phone,
            'password': active_user.password,
        }

        response = api_client.post(url, data, format='json')
        token = response.json()['success']
        return {
            'token': token,
            'user_email': active_user.email,
            'user_instance': active_user,
        }

    return _user
