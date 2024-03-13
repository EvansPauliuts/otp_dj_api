from core.models import ChoiceField
from core.models import GenericModel
from core.models import PrimaryStatusChoices
from core.models import TimeStampedModel
from core.models import TimezoneChoices
from core.models import UUIDModel
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import GroupManager
from django.contrib.auth.models import Permission
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.db import transaction
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from localflavor.us.models import USZipCodeField

from apps.accounts import tasks
from apps.accounts.services import profile
from apps.accounts.utils import PhoneValidator
from apps.accounts.validators import validate_org_timezone

from .business import BusinessUnit
from .department import Department
from .job import JobTitle
from .organization import Organization


class CustomGroup(TimeStampedModel):
    name = models.CharField(max_length=150)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
    )
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name='groups',
        related_query_name='group',
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='groups',
        related_query_name='group',
    )

    objects = GroupManager()

    class Meta:
        db_table = 'a_group'
        db_table_comment = 'Store the groups that a user belongs to.'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'organization',
                name='unique_group_organization',
            ),
        ]

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class CustomPermissionMixin(PermissionsMixin):
    groups = models.ManyToManyField(
        CustomGroup,
        blank=True,
        related_name='user_set',
        related_query_name='user',
    )

    class Meta:
        abstract = True

    def get_all_permissions(self, obj=None):
        custom_groups = self.groups.all()
        group_permissions = Permission.objects.filter(customgroup__in=custom_groups)
        user_permissions = Permission.objects.filter(user=self)
        permissions = group_permissions.union(user_permissions)
        return set(permissions.values_list('codename', flat=True).order_by())

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True

        app_label, codename = perm.split('.')

        if self.user_permissions.filter(
            codename=codename,
            content_type__app_label=app_label,
        ).exists():
            return True

        return self.groups.filter(
            permissions__codename=codename,
            content_type__app_label=app_label,
        )


class UserManager(BaseUserManager):
    def create_user(
        self,
        username,
        email,
        password=None,
        **extra_fields,
    ):
        if not username:
            raise ValueError('The username must be set')
        if not email:
            raise ValueError('The email must be set')

        user = self.model(
            username=username.lower(),
            email=self.normalize_email(email),
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self,
        username,
        email,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            username,
            email,
            password,
            **extra_fields,
        )


class User(UUIDModel, AbstractBaseUser, CustomPermissionMixin):
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name='users',
        related_query_name='user',
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        related_query_name='user',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='users',
        related_query_name='user',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_dev_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    online = models.BooleanField(default=False)
    timezone = ChoiceField(
        default=TimezoneChoices.EASTERN,
        choices=TimezoneChoices,
        validators=[validate_org_timezone],
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        null=True,
    )
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'user'
        permissions = (('accounts.view_all_users', 'Can view all users'),)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse(
            'accounts:users-detail',
            kwargs={'pk': self.pk},
        )

    def update_user(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()


class UserProfile(GenericModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        related_query_name='profiles',
    )
    job_title = models.ForeignKey(
        JobTitle,
        on_delete=models.PROTECT,
        related_name='profile',
        related_query_name='profiles',
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(
        upload_to='user_profiles/pictures/',
        blank=True,
        null=True,
    )
    thumbnail = models.ImageField(
        upload_to='user_profiles/thumbnails/',
        blank=True,
        null=True,
    )
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=5)
    zip_code = USZipCodeField()
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[PhoneValidator()],
    )
    is_phone_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_profile'
        db_table_comment = 'Stores additional information for a related user'

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()

        super().save(*args, **kwargs)

        if self.profile_picture and not self.thumbnail:
            transaction.on_commit(
                lambda: tasks.generate_thumbnail_task.delay(profile_id=str(self.id)),
            )

    def get_absolute_url(self):
        return reverse(
            'accounts:profile-view',
            kwargs={'pk': self.pk},
        )

    def update_profile(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def clean(self):
        if self.job_title.status == PrimaryStatusChoices.INACTIVE:
            raise ValidationError(
                {
                    'title': 'The selected job title is not active. '
                    'Please select a different job title.',
                },
                code='invalid',
            )

    @property
    def get_user_profile_pic(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/media/avatars/unknown.avif'

    @cached_property
    def get_full_address_combo(self):
        return (
            f'{self.address_line_1} {self.address_line_2} '
            f'{self.city} {self.state} {self.zip_code}'
        )

    @cached_property
    def get_user_city_state(self):
        return f'{self.city}, {self.state}'

    @cached_property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class Token(UUIDModel, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tokens',
        related_query_name='token',
    )
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(blank=True, null=True)
    last_used = models.DateTimeField(null=True, blank=True)
    key = models.CharField(
        max_length=40,
        unique=True,
        validators=[MinLengthValidator(40)],
    )

    class Meta:
        db_table = 'auth_token'
        db_table_comment = 'Stores the token for a user.'

    def __str__(self) -> str:
        return f'{self.key[:10]} ({self.user.username})'

    def save(self, *args, **kwargs) -> None:
        if not self.key:
            self.key = profile.generate_key()

        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        return self.expires is not None and timezone.now() >= self.expires


class UserFavorite(GenericModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        related_query_name='favorite',
    )
    page = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_favorite'
        db_table_comment = 'Stores the pages favorited by a user.'

    def __str__(self) -> str:
        return f'{self.page} ({self.user.username})'

    def get_absolute_url(self) -> str:
        return reverse(
            'accounts:user-favorite-detail',
            kwargs={'pk': self.pk},
        )
