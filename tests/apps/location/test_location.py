import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status

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
        assert response.data['location_contacts'][0]['phone'] == '+375 (44) 444-44-44'

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

    def test_post_location_with_comments_and_contacts(
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
                'location_contacts': [
                    {
                        'name': 'string',
                        'email': 'string@test.com',
                        'phone': '+375 (44) 444-44-44',
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
        assert response.data['location_contacts'][0]['email'] == 'string@test.com'
        assert response.data['location_contacts'][0]['name'] == 'string'
        assert response.data['location_contacts'][0]['phone'] == '+375 (44) 444-44-44'

    def test_put_location_with_comments_and_contacts(
        self,
        api_client,
        organization,
        business_unit,
        comment_type,
        location,
        user,
    ):
        location.refresh_from_db()

        response = api_client.put(
            reverse('locations:locations-detail', kwargs={'pk': location.id}),
            data={
                'organization': organization.id,
                'business_unit': business_unit.id,
                'code': 'LOCATION',
                'name': 'test location',
                'address_line_1': 'string',
                'city': 'string',
                'state': 'NC',
                'zip_code': '12345',
                'location_comments': [
                    {
                        'comment_type': comment_type.id,
                        'comment': 'this is a test comment for now for the location',
                        'entered_by': user.id,
                    },
                ],
                'location_contacts': [
                    {
                        'name': 'test_contact',
                        'email': 'test2@test.com',
                        'phone': '+375 (44) 444-44-44',
                    },
                ],
            },
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 'LOCATION'
        assert response.data['name'] == 'test location'
        assert response.data['address_line_1'] == 'string'
        assert response.data['city'] == 'string'
        assert response.data['state'] == 'NC'
        assert response.data['zip_code'] == '12345'
        assert response.data['location_comments'][0]['comment_type'] == comment_type.id
        assert (
            response.data['location_comments'][0]['comment']
            == 'this is a test comment for now for the location'
        )
        assert response.data['location_contacts'][0]['name'] == 'test_contact'
        assert response.data['location_contacts'][0]['email'] == 'test2@test.com'
        assert response.data['location_contacts'][0]['phone'] == '+375 (44) 444-44-44'

    def test_cannot_delete_location(
        self,
        api_client,
        location,
    ):
        response = api_client.delete(
            reverse('locations:locations-detail', kwargs={'pk': location.id}),
        )

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response.data['errors'][0]['detail'] == 'Method "DELETE" not allowed.'

    def test_location_contact_phone_number(self, location_contact):
        location_contact.phone = '+375'

        with pytest.raises(ValidationError) as excinfo:
            location_contact.full_clean()

        assert (
            excinfo.value.message_dict['phone'][0]
            == 'Phone number must be in the format: +375 (XX) XXX-XX-XX'
        )
