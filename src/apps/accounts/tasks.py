from celery import shared_task
from core.exceptions import ServiceException

# from celery import shared_task
from django.shortcuts import get_object_or_404

from apps.accounts import services
from apps.accounts.models.account import UserProfile


@shared_task(
    name='generate_thumbnail',
    bind=True,
    max_retries=5,
    default_retry_delay=60,
)
def generate_thumbnail_task(self, *, profile_id):
    try:
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        services.generate_thumbnail(size=(100, 100), user_profile=user_profile)
    except ServiceException as exc:
        raise self.retry(exc=exc) from exc
