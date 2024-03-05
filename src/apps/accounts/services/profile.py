import logging
import secrets

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image
from PIL import UnidentifiedImageError

from core.utils.helpers import optimize_image

log = logging.getLogger(__name__)


def generate_key() -> str:
    return secrets.token_hex(20)


def generate_thumbnail(
    *,
    user_profile,
    size,
):
    if not user_profile.profile_picture:
        log.info('User doesn\'t have a profile picture. Skipping thumbnail generation.')
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
            f'Uploaded image for {user_profile.user.username} '
            f'is invalid. Exception: {exc}'
        )
        raise ValidationError(
            {'profile_picture': 'The image is invalid. Please try again.'},
            code='invalid',
        ) from exc
    except* Exception as exc:
        log.exception(f'Failed to generate thumbnail for {user_profile.user.username}.')
        raise exc
