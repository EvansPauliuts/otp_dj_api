import base64
import logging
import os
import re

import pyotp
from django.conf import settings
from django.core.cache import cache
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.permissions import BasePermission

from apps.users.common import SystemRoleEnum

logger = logging.getLogger(__name__)
# client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def is_admin_user(user):
    return user.is_admin or SystemRoleEnum.ADMIN in user.roles


class IsAdmin(BasePermission):
    message = 'Only Admins are authorized to perform this action.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return is_admin_user(request.user)


def send_sms(message, phone):
    logger.info({'body': message, 'from': 'm', 'to': phone})
    # client.messages.create(
    #     body=message,
    #     from_=settings.TWILIO_PHONE_NUMBER,
    #     to=phone,
    # )
    return


def clean_phone(number):
    number_pattern = re.compile(
        r'^\+375(\s+)?\(?(17|29|33|44)\)?(\s+)?[0-9]{3}-?[0-9]{2}-?[0-9]{2}$'
    )
    result = number_pattern.match(number)
    if result:
        return number
    else:
        raise serializers.ValidationError(
            {
                'phone': 'Incorrect phone number.',
            }
        )


def generate_otp():
    totp = pyotp.TOTP(base64.b32encode(os.urandom(16)).decode('utf-8'))
    otp = totp.now()
    return otp


class PhoneValidator(RegexValidator):
    regex = r'^\+375(\s+)?\(?(17|29|33|44)\)?(\s+)?[0-9]{3}-?[0-9]{2}-?[0-9]{2}$'
    message = 'Phone number must be in the format: +375 (XX) XXX-XX-XX'


def delete_cache(key_prefix: str):
    keys_pattern = (
        f'views.decorators.cache.cache_*.{key_prefix}.*'
        f'.{settings.LANGUAGE_CODE}.{settings.TIME_ZONE}'
    )
    cache.delete_pattern(keys_pattern)
