import uuid

from django.core import checks
from django.db import models
from django.db.models import CharField
from django.utils import timezone


class UUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    class Meta:
        abstract = True


class Timestamped(UUIDModel, models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        abstract = True

    @property
    def changed(self):
        return bool(self.updated)

    def save(self, *args, **kwargs):  # noqa: DJ012
        if self.pk:
            self.updated = timezone.now()
        return super().save(*args, **kwargs)


class DefaultModel(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return getattr(self, 'name', super().__str__())


class TimeStampedModel(DefaultModel, Timestamped):
    class Meta:
        abstract = True


class PrimaryStatusChoices(models.TextChoices):
    ACTIVE = 'A', 'Active'
    INACTIVE = 'I', 'Inactive'


class GenericModel(TimeStampedModel):
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        related_query_name='%(class)s',
    )
    business_unit = models.ForeignKey(
        'accounts.BusinessUnit',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        related_query_name='%(class)s',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ChoiceField(CharField):
    description = 'Choice Field'

    def __init__(
        self,
        *args,
        db_collation=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.db_collation = db_collation
        if self.choices:
            self.max_length = max(len(choice[0]) for choice in self.choices)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._validate_choices_attribute(**kwargs),
        ]

    def _validate_choices_attribute(self, **kwargs):
        if self.choices is None:
            return [
                checks.Error(
                    'ChoiceField must define a `choice` attribute.',
                    hint='Add a `choice` attribute to the ChoiceField.',
                    obj=self,
                    id='fields.E120',
                ),
            ]
        return []


class Weekdays(models.IntegerChoices):
    MONDAY = 0, 'Monday'
    TUESDAY = 1, 'Tuesday'
    WEDNESDAY = 2, 'Wednesday'
    THURSDAY = 3, 'Thursday'
    FRIDAY = 4, 'Friday'
    SATURDAY = 5, 'Saturday'
    SUNDAY = 6, 'Sunday'


class TimezoneChoices(models.TextChoices):
    PACIFIC = 'America/Los_Angeles', 'Pacific'
    MOUNTAIN = 'America/Denver', 'Mountain'
    CENTRAL = 'America/Chicago', 'Central'
    EASTERN = 'America/New_York', 'Eastern'


class StatusChoices(models.TextChoices):
    NEW = 'N', 'New'
    IN_PROGRESS = 'P', 'In Progress'
    COMPLETED = 'C', 'Completed'
    HOLD = 'H', 'Hold'
    BILLED = 'B', 'Billed'
    VOIDED = 'V', 'Voided'


class DefaultModel(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return getattr(self, 'name', super().__str__())


class TimeStampedModel(DefaultModel, Timestamped):
    class Meta:
        abstract = True
