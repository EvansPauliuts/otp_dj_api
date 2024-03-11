import logging
import secrets

from core.utils.helpers import optimize_image
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image
from PIL import UnidentifiedImageError

log = logging.getLogger(__name__)


def generate_key() -> str:
    return secrets.token_hex(20)


def generate_thumbnail(
    *,
    user_profile,
    size,
):
    if not user_profile.profile_picture:
        log.info("User doesn't have a profile picture. Skipping thumbnail generation.")
        user_profile.thumbnail = None
        return

    try:
        img = Image.open(user_profile.profile_picture)
        optimized_img = optimize_image(img, size)

        user_profile.thumbnail = ContentFile(
            optimized_img.getvalue(),
            f'{user_profile.user.username}_thumbnail.webp',
        )

        user_profile.save()

        img.close()
        optimized_img.close()

    except* UnidentifiedImageError as exc:
        log.error(
            'Uploaded image for %s is invalid. Exception: %s',
            user_profile.user.username,
            exc_info=exc,
        )
        raise ValidationError(
            {'profile_picture': 'The image is invalid. Please try again.'},
            code='invalid',
        ) from exc
    except* Exception as exc:
        log.exception(
            'Failed to generate thumbnail for %s.',
            user_profile.user.username,
        )
        raise exc
