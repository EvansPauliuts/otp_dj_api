# import pytest
# from django.urls import reverse
# from apps.users.models import PendingUser
#
# from tests.conftest import api_client_with_credentials
#
# pytestmark = pytest.mark.django_db
#
#
# class TestUser:
#     user_list_endpoint = reverse('users:user-list')
#
#     def test_create_user(self, api_client, mocker):
#         mock_send_verification_otp = mocker.patch(
#             'apps.users.tasks.send_phone_notification.delay'
#         )
#
#         data = {
#             'phone': '+375 44 444-44-42',
#             'password': 'hello@@@111',
#         }
#
#         response = api_client.post(self.user_list_endpoint, data, format='json')
#         assert response.status_code == 200
#
#         pending_user = PendingUser.objects.get(phone=data['phone'])
#
#         message_info = {
#             'message': f'Account Verification!\nYour OTP for BotoApp is '
#             f'{pending_user.verification_code}'
#             f'.\nIt expires in 10 minutes',
#             'phone': data['phone'],
#         }
#
#         mock_send_verification_otp.assert_called_once_with(message_info)
#
#     def test_deny_create_user_duplicate_phone(self, api_client, active_user):
#         data = {
#             'phone': active_user.phone,
#             'password': '<PASSWORD>',
#         }
#         response = api_client.post(self.user_list_endpoint, data, format='json')
#         assert response.status_code == 400
#
#     def test_admin_retrieve_all_users(
#         self,
#         api_client,
#         user_factory,
#         authenticate_user,
#     ):
#         user_factory.create_batch(3)
#         user = authenticate_user(is_admin=True)
#         token = user['token']
#         api_client_with_credentials(token, api_client)
#         response = api_client.get(self.user_list_endpoint)
#         assert response.status_code == 200
#         assert response.json()['total'] == 4
#
#     def test_non_admin_retrieve_data(
#         self,
#         api_client,
#         user_factory,
#         authenticate_user,
#     ):
#         user_factory.create_batch(3)
#         user = authenticate_user(is_admin=False)
#         token = user['token']
#         api_client_with_credentials(token, api_client)
#         response = api_client.get(self.user_list_endpoint)
#         assert response.status_code == 200
#         assert response.json()['total'] == 1
#
#     def test_admin_update_all_users(
#         self,
#         api_client,
#         user_factory,
#         authenticate_user,
#     ):
#         app_user = user_factory(firstname='First')
#         user = authenticate_user(is_admin=True)
#         token = user['token']
#         data = {
#             'first_name': 'Nike',
#         }
#         api_client_with_credentials(token, api_client)
#         url = reverse('users:user-detail', kwargs={'pk': app_user.id})
#         response = api_client.patch(url, data, format='json')
#         assert response.status_code == 200
#         assert response.json()['first_name'] == data['first_name']
#
#     def test_admin_delete_user(
#         self,
#         api_client,
#         user_factory,
#         authenticate_user,
#     ):
#         app_user = user_factory(firstname='First')
#         user = authenticate_user(is_admin=True)
#         token = user['token']
#         api_client_with_credentials(token, api_client)
#         url = reverse('users:user-detail', kwargs={'pk': app_user.id})
#         response = api_client.delete(url, format='json')
#         assert response.status_code == 204
#
#     def test_deny_delete_to_non_admin(
#         self,
#         api_client,
#         user_factory,
#         authenticate_user,
#     ):
#         app_user = user_factory(firstname='First')
#         user = authenticate_user(is_admin=False)
#         token = user['token']
#         api_client_with_credentials(token, api_client)
#         url = reverse('users:user-detail', kwargs={'pk': app_user.id})
#         response = api_client.delete(url, format='json')
#         assert response.status_code == 403
#
#     def test_non_admin_update_personal_data(
#         self,
#         api_client,
#         authenticate_user,
#     ):
#         user = authenticate_user(is_admin=False)
#         user_instance = user['user_instance']
#         token = user['token']
#         data = {
#             'first_name': 'Nike',
#         }
#         api_client_with_credentials(token, api_client)
#         url = reverse('users:user-detail', kwargs={'pk': user_instance.id})
#         response = api_client.patch(url, data, format='json')
#         assert response.status_code == 200
#         assert response.json()['first_name'] == data['first_name']
