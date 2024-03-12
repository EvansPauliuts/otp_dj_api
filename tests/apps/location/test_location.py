import pytest

# from django.core.exceptions import ValidationError
# from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

# from apps.location.models import CommentType
# from apps.accounts.models import BusinessUnit, Organization

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestLocation:
    api_endpoint = reverse('locations:locations-list')

    def test_location_creation(self, location):
        assert location is not None

    def test_location_update(self, location):
        location.name = 'New name'
        location.save()

        assert location.name == 'New name'

    def test_post_location(
        self,
        api_client,
        organization,
        business_unit,
    ):
        response = api_client.post(
            self.api_endpoint,
            data={
                'organization': organization.id,
                'business_unit': business_unit.id,
                'code': 'string',
                'name': 'string',
                'address_line_1': 'string',
                'city': 'string',
                'state': 'NC',
                'zip_code': '12345',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'string'
        assert response.data['code'] == 'string'
        assert response.data['address_line_1'] == 'string'
        assert response.data['city'] == 'string'
        assert response.data['state'] == 'NC'
        assert response.data['zip_code'] == '12345'

    def test_post_location_with_contacts(
        self,
        api_client,
        organization,
        business_unit,
    ):
        response = api_client.post(
            self.api_endpoint,
            data={
                'organization': organization.id,
                'business_unit': business_unit.id,
                'code': 'string',
                'name': 'string',
                'address_line_1': 'string',
                'city': 'string',
                'state': 'NC',
                'zip_code': '12345',
                'location_contacts': [
                    {
                        'name': 'string',
                        'email': 'string@test.com',
                        'phone': '+375 (44) 444-44-44',
                        'fax': '+375 (44) 444-44',
                    },
                ],
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'string'
        assert response.data['code'] == 'string'
        assert response.data['address_line_1'] == 'string'
        assert response.data['city'] == 'string'
        assert response.data['state'] == 'NC'
        assert response.data['zip_code'] == '12345'
        assert response.data['location_contacts'][0]['name'] == 'string'
        assert response.data['location_contacts'][0]['email'] == 'string@test.com'
        assert response.data['location_contacts'][0]['phone'] == '+375 (44) 444-44'
        assert response.data['location_contacts'][0]['fax'] == '+375 (44) 444-44'

    def test_post_location_with_comments(
        self,
        api_client,
        organization,
        business_unit,
        comment_type,
        user,
    ):
        response = api_client.post(
            self.api_endpoint,
            data={
                'organization': organization.id,
                'business_unit': business_unit.id,
                'code': 'string',
                'name': 'string',
                'address_line_1': 'string',
                'city': 'string',
                'state': 'NC',
                'zip_code': '12345',
                'location_comments': [
                    {
                        'comment_type': comment_type.id,
                        'comment': 'this is a test comment for now.',
                        'entered_by': user.id,
                    },
                ],
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'string'
        assert response.data['name'] == 'string'
        assert response.data['address_line_1'] == 'string'
        assert response.data['city'] == 'string'
        assert response.data['state'] == 'NC'
        assert response.data['zip_code'] == '12345'
        assert response.data['location_comments'][0]['comment_type'] == comment_type.id
        assert (
            response.data['location_comments'][0]['comment']
            == 'this is a test comment for now.'
        )
