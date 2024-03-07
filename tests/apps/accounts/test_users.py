import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


# def test_get(api_client) -> None:
#     """
#     Test get users
#     """
#     response = api_client.get("/api/users/")
#     assert response.status_code == 200


class TestUser:
    user_list_endpoint = reverse('users:users-list')
    api_endpoint = '/api/v1/users/'

    def test_get_user(self, api_client):
        response = api_client.get(self.api_endpoint, format='json')
        print(response.data)
        assert response.status_code == status.HTTP_200_OK

    def test_get_by_id(self, api_client, user_api):
        response = api_client.get(
            f'{self.api_endpoint}{user_api.data["id"]}', format='json'
        )
        assert response.status_code == status.HTTP_200_OK
