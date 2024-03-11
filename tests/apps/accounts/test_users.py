import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from tests.factories.apps.accounts import JobTitleFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestUser:
    api_endpoint = reverse('users:users-list')

    def test_get_user(self, api_client):
        response = api_client.get(self.api_endpoint, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_get_by_id(self, api_client, user_api):
        response = api_client.get(
            reverse('users:users-detail', kwargs={'pk': user_api.data['id']}),
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK

    def test_create_success(self, api_client, organization, business_unit):
        job_title = JobTitleFactory()

        payload = {
            'business_unit': business_unit.id,
            'organization': organization.id,
            'username': 'test_username',
            'email': 'test_user@example.com',
            'profile': {
                'business_unit': business_unit.id,
                'organization': organization.id,
                'first_name': 'test',
                'last_name': 'user',
                'address_line_1': 'test',
                'city': 'test',
                'state': 'NC',
                'zip_code': '12345',
                'job_title': job_title.id,
            },
        }

        response = api_client.post(self.api_endpoint, payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'password' not in response.data
        assert response.data['username'] == payload['username']
        assert response.data['email'] == payload['email']

    def test_user_with_email_exists_error(self, api_client, organization, business_unit):
        payload = {
            'username': 'test_user2',
            'email': 'test_user@example.com',
            'profile': {
                'first_name': 'test',
                'last_name': 'user',
                'address_line_1': 'test',
                'city': 'test',
                'zip_code': '12345',
                'state': 'NC',
            },
        }

        User.objects.create_user(
            organization=organization,
            business_unit=business_unit,
            username=payload['username'],
            email=payload['email'],
        )

        response = api_client.post(self.api_endpoint, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_put(self, user_api, api_client, organization):
        response = api_client.put(
            reverse('users:users-detail', kwargs={'pk': user_api.data['id']}),
            data={
                'organization': organization.id,
                'username': 'test2342',
                'email': 'test@test.com',
                'profile': {
                    'organization': organization.id,
                    'first_name': 'test',
                    'last_name': 'user',
                    'address_line_1': 'test',
                    'city': 'test',
                    'state': 'NC',
                    'zip_code': '12345',
                },
            },
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'test2342'
        assert response.data['email'] == 'test@test.com'
        assert response.data['profile']['first_name'] == 'Test'
        assert response.data['profile']['last_name'] == 'User'
        assert response.data['profile']['address_line_1'] == 'test'
        assert response.data['profile']['city'] == 'test'
        assert response.data['profile']['zip_code'] == '12345'
        assert response.data['profile']['state'] == 'NC'
        assert 'password' not in response.data

    def test_user_delete(self, user_api, api_client):
        response = api_client.delete(
            reverse(
                'users:users-detail',
                kwargs={'pk': user_api.data['id']},
            )
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
