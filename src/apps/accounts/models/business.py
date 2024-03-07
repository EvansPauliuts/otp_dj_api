from django.db import models
from core.models import TimeStampedModel
from django.urls import reverse
from django.utils import timezone
from localflavor.us.models import USZipCodeField
from django.core.validators import FileExtensionValidator
from django.db.models.functions import Lower

from apps.accounts.utils import PhoneValidator, business_unit_contract_upload_to


class BusinessUnit(TimeStampedModel):
    class BusinessUnitStatusChoices(models.TextChoices):
        ACTIVE = 'A', 'Active'
        INACTIVE = 'I', 'Inactive'
        SUSPENDED = 'S', 'Suspended'

    status = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    entity_key = models.CharField(max_length=10, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=5)
    zip_code = USZipCodeField(blank=True)
    contact_email = models.EmailField(max_length=255, blank=True)
    contact_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[PhoneValidator()],
    )
    description = models.TextField(blank=True)
    paid_until = models.DateField(null=True, blank=True)
    free_trial = models.BooleanField(default=False)
    billing_info = models.JSONField(null=True, blank=True)
    tax_id = models.CharField(max_length=255, blank=True)
    legal_name = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_suspended = models.BooleanField(default=False)
    suspension = models.TextField(blank=True)
    contract = models.FileField(
        upload_to=business_unit_contract_upload_to,
        validators=[FileExtensionValidator(['pdf'])],
        blank=True,
    )

    class Meta:
        db_table = 'business_unit'
        db_table_comment = 'Stores information about the Business Unit.'
        constraints = [
            models.UniqueConstraint(
                Lower('entity_key'),
                name='unique_business_unit_entity_key',
            )
        ]

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        if not self.entity_key:
            base_key = self.name.replace(' ', '')[:8].upper()
            counter = 1
            entity_key = f'{base_key}-{counter:02d}'

            while self.__class__.objects.filter(entity_key=entity_key).exists():
                counter += 1
                entity_key = f'{base_key}-{counter:02d}'

            self.entity_key = entity_key

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'accounts:businessunits-detail',
            kwargs={'pk', self.pk},
        )

    @property
    def paid(self):
        return bool(self.paid_until and self.paid_until > timezone.now().date())
