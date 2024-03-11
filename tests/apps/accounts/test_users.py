from io import BytesIO
from unittest.mock import patch

import pytest
from apps.accounts.api.serializers import UserSerializer
from apps.accounts.selectors import get_user_auth_token_from_request
from apps.accounts.selectors import get_users_by_organization_id
from apps.accounts.tasks import generate_thumbnail_task
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from tests.factories.apps.accounts import JobTitleFactory
from tests.factories.apps.accounts import UserFactory

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

    def test_user_with_email_exists_error(
        self,
        api_client,
        organization,
        business_unit,
    ):
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
            ),
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None

    def test_user_cannot_change_password_on_update(
        self,
        user,
        business_unit,
        organization,
    ):
        payload = {
            'organization': organization.id,
            'business_unit': business_unit.id,
            'username': 'test_user',
            'email': 'test_user@example.com',
            'password': 'test_password1234%',
            'profile': {
                'first_name': 'test',
                'last_name': 'user',
                'address_line_1': 'test',
                'city': 'test_city',
                'state': 'NC',
                'zip_code': '12345',
            },
        }

        with pytest.raises(ValidationError) as ex:
            UserSerializer.update(
                self=UserSerializer,
                instance=user,
                validated_data=payload,
            )

        assert (
            'Password cannot be changed using this endpoint. '
            'Please use the change password endpoint.' in str(ex.value.detail)
        )
        # assert 'code="invalid"' in str(ex.value.detail)
        # assert ex.value.detail_code == 'invalid'

    def test_inactive_user_cannot_login(self, api_client, user_api):
        user = User.objects.get(id=user_api.data['id'])
        user.is_active = False
        user.save()

        response = api_client.post(
            reverse('users:provision_token'),
            data={
                'username': user_api.data['username'],
                'password': '<PASSWORD>',
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_user(self, unauthenticated_api_client, user_api):
        user = User.objects.get(id=user_api.data['id'])
        user.set_password('trashuser12345%')
        user.save()

        # response = unauthenticated_api_client.post(
        #     reverse('users:provision_token'),
        #     data={
        #         'username': user_api.data['username'],
        #         'password': 'trashuser12345%',
        #     },
        # )

        # assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.online is True
        assert user.last_login

    def test_logout_user(self, api_client, user_api):
        response = api_client.post(reverse('users:logout'))
        assert response.status_code == status.HTTP_204_NO_CONTENT

        user = User.objects.get(id=user_api.data['id'])
        assert user.online is False

    def test_reset_password(self, unauthenticated_api_client, user):
        response = unauthenticated_api_client.post(
            reverse('users:reset_password'),
            data={'email': user.email},
        )
        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data['message']
            == 'Password reset successfully. Please check your email for new password'
        )
        # assert len(mail.outbox) == 1
        # assert mail.outbox[0].subject == 'Your password has been reset'

    def test_validate_reset_password(self, unauthenticated_api_client):
        response = unauthenticated_api_client.post(
            reverse('users:reset_password'),
            data={'email': 'random@test.com'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data['email'][0]
            == 'No user found with the given email exists. Please try again.'
        )

    def test_validate_reset_password_with_invalid_email(
        self,
        unauthenticated_api_client,
    ):
        response = unauthenticated_api_client.post(
            reverse('users:reset_password'),
            data={'email': 'random'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['email'][0] == 'Enter a valid email address.'

    def test_validate_reset_password_with_inactive_user(
        self,
        unauthenticated_api_client,
        user,
    ):
        user.is_active = False
        user.save()

        response = unauthenticated_api_client.post(
            reverse('users:reset_password'),
            data={'email': user.email},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['email'][0] == 'This user is not active. Please try again.'

    def test_change_email(self, user):
        new_password_ = 'new_password1234%'
        user.set_password(new_password_)
        user.save()
        user.refresh_from_db()

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            reverse('users:change_email'),
            data={
                'email': 'another_test@test.com',
                'current_password': 'new_password1234%',
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Email successfully updated.'

    def test_change_email_with_invalid_password(self, user):
        new_password_ = 'new_password1234%'
        user.set_password(new_password_)
        user.save()
        user.refresh_from_db()

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            reverse('users:change_email'),
            data={
                'email': 'test_email@test.com',
                'current_password': 'wrong_password',
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data['current_password'][0]
            == 'Current password is incorrect. Please try again.'
        )

    def test_change_email_with_same_email(self, user):
        new_password_ = 'new_password1234%'
        user.set_password(new_password_)
        user.save()
        user.refresh_from_db()

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            reverse('users:change_email'),
            data={
                'email': user.email,
                'current_password': 'new_password1234%',
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data['email'][0]
            == 'New email cannot be the same as the current email.'
        )

    def test_change_email_with_other_users_email(self, user):
        new_password_ = 'new_password1234%'
        user.set_password(new_password_)
        user.save()
        user.refresh_from_db()

        user_2 = UserFactory(
            username='other_user',
            email='test_another@test.com',
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            reverse('users:change_email'),
            data={
                'email': user_2.email,
                'current_password': 'new_password1234%',
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['email'][0] == 'A user with this email already exists.'

    def test_validate_password_not_allowed_on_post(
        self,
        api_client,
        organization,
        job_title,
    ):
        payload = {
            'organization': organization.id,
            'username': 'test_user_4',
            'email': 'test_user@test.com',
            'password': 'test_password',
            'profile': {
                'organization': organization.id,
                'first_name': 'test',
                'last_name': 'user',
                'address_line_1': 'test',
                'city': 'test city',
                'state': 'NC',
                'zip_code': '12345',
                'job_title': job_title.id,
            },
        }

        response = api_client.post(
            self.api_endpoint,
            payload,
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['errors'][0]['attr'] == 'email'
        assert (
            response.data['errors'][0]['detail']
            == 'user with this email already exists.'
        )

    @pytest.mark.skip
    @patch('apps.accounts.tasks.generate_thumbnail_task')
    def test_create_thumbnail_task(self, user_thumbnail, user_profile):
        image = Image.new('RGB', (100, 100))
        image_file = BytesIO()
        image.save(image_file, 'png')
        image_file.seek(0)
        image = SimpleUploadedFile('test.png', image_file.getvalue())

        user_profile.profile_picture.save(
            'test.png',
            ContentFile(image_file.getvalue()),
        )

        generate_thumbnail_task(profile_id=user_profile.id)

        user_thumbnail.assert_called_once_with(
            size=(100, 100),
            user_profile=user_profile,
        )
        user_thumbnail.assert_called_once()

    def test_get_user_by_org_id_selector(self, user):
        user = get_users_by_organization_id(organization_id=user.organization.id)
        assert user is not None

    def test_get_user_auth_token_from_request(self, user):
        request = RequestFactory().get(self.api_endpoint)
        request.user = user

        token = get_user_auth_token_from_request(request=request)
        assert token is not None
