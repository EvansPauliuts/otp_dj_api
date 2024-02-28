import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.users.models import PendingUser
from core.celery import celery

from .utils import send_sms

logger = logging.getLogger(__name__)


@celery.task(name='users.send_me')
def send_phone_notification(user_data):
    send_sms(
        user_data['message'],
        user_data['phone'],
    )


@shared_task(serialize='json')
def delete_old_activation_codes():
    time_minutes_old = timezone.now() - timedelta(minutes=5)
    old_codes = PendingUser.objects.filter(created=time_minutes_old)

    for code in old_codes:
        code.delete()

    if old_codes.exists():
        logger.info('DELETE!!!')
        return {'status': True, 'message': 'User not activation code old'}
    return {'message': 'Not delete!'}
