from celery import shared_task
from core.exceptions import ServiceExceptionError
from django.shortcuts import get_object_or_404

from apps.accounts.models import UserProfile
from apps.accounts.services import profile


@shared_task(
    name='generate_thumbnail',
    bind=True,
    max_retries=5,
    default_retry_delay=60,
)
def generate_thumbnail_task(self, *, profile_id):
    try:
        user_profile = get_object_or_404(UserProfile, id=profile_id)
        profile.generate_thumbnail(size=(100, 100), user_profile=user_profile)
    except ServiceExceptionError as exc:
        raise self.retry(exc=exc) from exc
