from datetime import timezone, datetime
from django.db import models
from django.conf import settings

from core.models import AuditableModel
from core.utils import PhoneValidator


class PendingUser(AuditableModel):
    phone = models.CharField(
        max_length=19,
        validators=[PhoneValidator],
    )
    verification_code = models.CharField(
        max_length=4,
        blank=True,
        null=True,
    )
    password = models.CharField(
        max_length=255,
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f'{self.phone} {self.verification_code}'

    def is_valid(self):
        lifespan_in_seconds = float(settings.OTP_EXPIRE_TIME * 60)
        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()

        if time_diff >= lifespan_in_seconds:
            return False
        return True
