from core.celery import celery

from .utils import send_sms


@celery.task(name='users.send_me')
def send_phone_notification(user_data):
    send_sms(
        user_data['message'],
        user_data['phone'],
    )
