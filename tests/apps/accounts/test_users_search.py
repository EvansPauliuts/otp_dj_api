import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestUsersSearch:
    api_endpoint = reverse('users:users-list')

    def test_search_username_list(self, api_client, user):
        response = api_client.get(
            self.api_endpoint + f'?search={user.username}',
            format='json',
        )

        assert len(response.data['results']) == 1

    def test_search_username_empty(self, api_client, user):
        wrong_user_name = f'{user.username}_wr'

        response = api_client.get(
            self.api_endpoint + f'?search={wrong_user_name}',
            format='json',
        )

        assert len(response.data['results']) == 0

    def test_search_email_list(self, api_client, user):
        response = api_client.get(
            self.api_endpoint + f'?search={user.email}',
            format='json',
        )

        assert len(response.data['results']) == 1

    def test_search_email_empty(self, api_client, user):
        wrong_email = 'test_1@test.com'

        response = api_client.get(
            self.api_endpoint + f'?search={wrong_email}',
            format='json',
        )

        assert len(response.data['results']) == 0
