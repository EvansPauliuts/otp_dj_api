import pytest

from django.urls import reverse

from .conftest import api_client_with_credentials
from api.models import PendingUser

pytestmark = pytest.mark.django_db


class TestUser:
    user_list_url = reverse('user:user-list')

    def test_create_user(self, api_client, mocker):
        mock_send_verification_otp = mocker.patch(
            'api.tasks.send_phone_notification.delay',
        )

        data = {
            'phone': '+375 44 444-44-44',
            'password': 'simplepass',
        }

        response = api_client.post(self.user_list_url, data)
        assert response.status_code == 200

        pending_user = PendingUser.objects.get(phone=data['phone'])
        message_info = {
            'message': f'Account Verification!\nYour OTP for BotoApp is {pending_user.verification_code}.\nIt expires in 10 minutes',
            'phone': data['phone'],
        }

        mock_send_verification_otp.assert_called_once_with(message_info)
