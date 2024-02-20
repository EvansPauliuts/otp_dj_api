import uuid

from datetime import timezone, datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import ArrayField

from .enums import ROLE_CHOICE, TOKEN_TYPE_CHOICE
from core.models import AuditableModel
from .utils import PhoneValidator
from .managers import CustomUserManager


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


def default_role():
    return ['CUSTOMER']


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        null=True,
        blank=True,
        unique=True,
    )
    password = models.CharField(
        max_length=255,
        null=True,
    )
    firstname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    lastname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    image = models.FileField(
        upload_to="users/",
        blank=True,
        null=True,
    )
    phone = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
    )
    is_locked = models.BooleanField(
        default=False,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=False,
    )
    is_admin = models.BooleanField(
        default=False,
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    verified = models.BooleanField(
        default=False,
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    roles = ArrayField(
        models.CharField(max_length=20, blank=True, choices=ROLE_CHOICE),
        default=default_role,
        size=6,
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.phone

    def save_last_login(self) -> None:
        self.last_login = datetime.now()
        self.save()


class Token(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    token = models.CharField(max_length=8)
    token_type = models.CharField(
        max_length=100,
        choices=TOKEN_TYPE_CHOICE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{str(self.user)} {self.token}'

    def is_valid(self):
        lifespan_in_seconds = float(settings.TOKEN_LIFESPAN * 60)
        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True

    def reset_user_password(self, password):
        self.user.set_password(password)
        self.user.save()
