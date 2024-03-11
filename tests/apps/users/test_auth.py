from datetime import UTC
from datetime import datetime
from datetime import timedelta

import pytest
import time_machine
from apps.users.common import SystemRoleEnum
from apps.users.common import TokenEnum
from apps.users.models import PendingUser
from apps.users.models import Token
from apps.users.models import User
from django.urls import reverse
from rest_framework import status

from tests.conftest import api_client_with_credentials

pytestmark = pytest.mark.django_db


class TestAuthEndpoints:
    initiate_password_reset_url = reverse('users:auth-initiate-password-reset')
    password_change_url = reverse('users:password_change-list')

    login_url = reverse('users:login')
    verify_account_url = reverse('users:auth-verify-account')
    create_password_reset_otp_url = reverse('users:auth-create-password')

    def test_user_login(
        self,
        api_client,
        active_user,
        auth_user_password,
    ):
        data = {
            'phone': active_user.phone,
            'password': active_user.password,
        }
        response = api_client.post(self.login_url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

        return_json = response.json()
        assert 'refresh' in return_json
        assert 'success' in return_json

    def test_deny_login_to_inactive_user(
        self,
        api_client,
        inactive_user,
        auth_user_password,
    ):
        data = {
            'phone': inactive_user.phone,
            'password': auth_user_password,
        }
        response = api_client.post(self.login_url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_deny_login_to_invalid_credentials(
        self,
        api_client,
        active_user,
    ):
        data = {
            'phone': active_user.phone,
            'password': '<PASSWORD>',
        }
        response = api_client.post(self.login_url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_password_reset_initiate(
        self,
        mocker,
        api_client,
        active_user,
    ):
        mock_send_reset_otp = mocker.patch(
            'apps.users.tasks.send_phone_notification.delay',
        )
        data = {
            'phone': active_user.phone,
        }
        response = api_client.post(
            self.initiate_password_reset_url,
            data,
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK

        mock_send_reset_otp.side_effect = print(
            'Sent to celery task:Password Reset SMS!',
        )

        token = Token.objects.get(
            user=active_user,
            token_type=TokenEnum.PASSWORD_RESET,
        )
        otp = token.token
        message_info = {
            'message': f'Password Reset!\nUse {otp} to reset your password.'
            f'\nIt expires in 10 minutes',
            'phone': active_user.phone,
        }
        mock_send_reset_otp.assert_called_once_with(message_info)

    def test_deny_initiate_password_reset(self, api_client):
        data = {
            'phone': '+375 44 444-44-44',
        }
        response = api_client.post(
            self.initiate_password_reset_url,
            data,
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_using_valid_old_password(
        self,
        api_client,
        authenticate_user,
        auth_user_password,
    ):
        user = authenticate_user()
        token = user['token']
        user_instance = user['user_instance']
        data = {
            'old_password': auth_user_password,
            'new_password': '<PASSWORD>',
        }
        api_client_with_credentials(token, api_client)
        response = api_client.post(self.password_change_url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

        user_instance.refresh_from_db()
        assert user_instance.check_password('<PASSWORD>')

    def test_deny_change_password_using_invalid_old_password(
        self,
        api_client,
        authenticate_user,
    ):
        user = authenticate_user()
        token = user['token']
        data = {
            'old_password': 'invalid',
            'new_password': '<PASSWORD>',
        }
        api_client_with_credentials(token, api_client)
        response = api_client.post(self.password_change_url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_deny_change_password_for_unathenticated_user(self, api_client):
        data = {
            'old_password': 'invalidpass',
            'new_password': 'new@@@@!!!',
        }
        response = api_client.post(self.password_change_url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_account_using_otp(self, api_client):
        pending_user = PendingUser.objects.create(
            phone='+375 44 444-44-44',
            verification_code=1234,
            password='<PASSWORD>',  # noqa: S106
        )
        data = {
            'otp': pending_user.verification_code,
            'phone': pending_user.phone,
        }
        response = api_client.post(self.verify_account_url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

        user_obj = User.objects.get(phone=pending_user.phone)
        assert user_obj.verified is True
        assert user_obj.is_active is True
        assert user_obj.roles == [SystemRoleEnum.CUSTOMER]

    def test_deny_verify_account_expired_otp(self, api_client):
        pending_user = PendingUser.objects.create(
            phone='+375 44 444-44-44',
            verification_code=1234,
            password='<PASSWORD>',  # noqa: S106
        )
        with time_machine.travel(datetime.now(UTC) + timedelta(minutes=10)):
            data = {
                'otp': pending_user.verification_code,
                'phone': pending_user.phone,
            }
            response = api_client.post(self.verify_account_url, data, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_deny_verify_account_using_invalid_otp(self, api_client):
        pending_user = PendingUser.objects.create(
            phone='+375 44 444-44-44',
            verification_code=1234,
            password='password',  # noqa: S106
        )
        data = {
            'otp': 3456,
            'phone': pending_user.phone,
        }
        response = api_client.post(self.verify_account_url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_new_password_using_valid_reset_otp(
        self,
        api_client,
        active_user,
        token_factory,
    ):
        token = token_factory(
            user=active_user,
            token_type=TokenEnum.PASSWORD_RESET,
        )
        data = {
            'otp': token.token,
            'new_password': 'new_pass_me',
        }
        response = api_client.post(
            self.create_password_reset_otp_url,
            data,
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK

        active_user.refresh_from_db()
        assert active_user.check_password('new_pass_me')

    def test_deny_create_new_password_using_invalid_reset_otp(
        self,
        api_client,
        active_user,
        token_factory,
    ):
        token_factory(
            token_type=TokenEnum.PASSWORD_RESET,
            user=active_user,
            token=1234,
        )
        data = {
            'otp': 4321,
            'new_password': 'new_pass_me',
        }
        response = api_client.post(
            self.create_password_reset_otp_url,
            data,
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
