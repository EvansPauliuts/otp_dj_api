from django.db import models
from core.models import TimeStampedModel
from django.urls import reverse
from localflavor.us.models import USZipCodeField
from django.utils.functional import cached_property

from apps.accounts.utils import PhoneValidator
from apps.accounts.validators import validate_org_timezone

from .business import BusinessUnit


class Organization(TimeStampedModel):
    class OrganizationType(models.TextChoices):
        ASSET = 'ASSET', 'Asset'
        BROKERAGE = 'BROKERAGE', 'Brokerage'
        BOTH = 'BOTH', 'Both'

    class LanguageChoices(models.TextChoices):
        ENGLISH = 'en', 'English'
        SPANISH = 'es', 'Spanish'

    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name='organizations',
    )
    name = models.CharField(max_length=255)
    scac_code = models.CharField(max_length=4)
    dot_number = models.PositiveIntegerField(null=True, blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=5)
    zip_code = USZipCodeField()
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[PhoneValidator()],
    )
    website = models.URLField(blank=True)
    org_type = models.CharField(
        max_length=10,
        choices=OrganizationType,
        default=OrganizationType.ASSET,
    )
    timezone = models.CharField(
        max_length=255,
        default='America/New_York',
        validators=[validate_org_timezone],
    )
    language = models.CharField(
        max_length=2,
        choices=LanguageChoices,
        default=LanguageChoices.ENGLISH,
    )
    currency = models.CharField(max_length=255, default='USD')
    date_format = models.CharField(max_length=255, default='MM/DD/YYYY')
    time_format = models.CharField(max_length=255, default='HH:mm')
    logo = models.ImageField(
        upload_to='organizations/logo/',
        null=True,
        blank=True,
    )
    token_expiration_days = models.PositiveIntegerField(default=30)

    class Meta:
        db_table = 'organization'
        db_table_comment = 'Stores information about the Organization.'
        permissions = (
            ('view_systemhealth', 'Can View System Health'),
            ('view_activesessions', 'Can View Active Sessions'),
            ('view_threads', 'Can View Active Threads'),
            ('view_activetriggers', 'Can View Active Triggers'),
            ('view_cachemanager', 'Can View Cache Manager'),
            ('view_admin_dashboard', 'Can View Admin Dashboard'),
        )

    def __str__(self):
        return f'{self.name} ({self.scac_code}'

    def save(self, *args, **kwargs):
        self.scac_code = self.scac_code.upper()
        self.name = self.name.title()
        super().save(**kwargs)

    def get_absolute_url(self):
        return reverse(
            'accounts:organizations-detail',
            kwargs={'pk': self.pk},
        )

    @cached_property
    def get_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    @cached_property
    def get_city_state_zip(self):
        return f'{self.city}, {self.state} {self.zip_code}'

    @cached_property
    def get_full_address(self):
        return f'{self.get_address} {self.get_city_state_zip}'
