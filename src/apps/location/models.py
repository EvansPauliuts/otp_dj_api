import textwrap

from colorfield.fields import ColorField
from core.models import ChoiceField
from core.models import GenericModel
from core.models import PrimaryStatusChoices
from core.models import TimeStampedModel
from core.utils.helpers import PhoneValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg
from django.db.models import DurationField
from django.db.models import ExpressionWrapper
from django.db.models import F
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.functional import cached_property
from localflavor.us.models import USZipCodeField

from apps.accounts.models import Depot

User = get_user_model()


class LocationCategory(GenericModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = ColorField(blank=True, null=True)

    class Meta:
        db_table = 'location_category'
        db_table_comment = 'Stores location category information.'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'organization',
                name='unique_location_category_name',
            ),
        ]

    def __str__(self):
        return textwrap.shorten(
            f'{self.name}: {self.description}',
            width=50,
            placeholder='...',
        )

    def get_absolute_url(self):
        return reverse('locations:location-detail', kwargs={'pk': self.pk})


class Location(GenericModel):
    status = ChoiceField(
        choices=PrimaryStatusChoices,
        default=PrimaryStatusChoices.ACTIVE,
    )
    code = models.CharField(max_length=10)
    location_category = models.ForeignKey(
        LocationCategory,
        on_delete=models.RESTRICT,
        related_name='location',
        related_query_name='locations',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255, db_index=True)
    depot = models.ForeignKey(
        Depot,
        on_delete=models.PROTECT,
        related_name='location',
        related_query_name='locations',
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=5)
    zip_code = USZipCodeField()
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    place_id = models.CharField(max_length=255, blank=True)
    is_geocoded = models.BooleanField(default=False)

    class Meta:
        db_table = 'location'
        db_table_comment = 'Stores location information for a related organization.'
        constraints = [
            models.UniqueConstraint(
                Lower('code'),
                'organization',
                name='unique_location_code_organization',
            ),
        ]

    def __str__(self):
        return textwrap.shorten(
            f'{self.code}: {self.name}',
            width=50,
            placeholder='...',
        )

    def get_absolute_url(self):
        return reverse('locations:location-detail', kwargs={'pk': self.pk})

    @cached_property
    def get_address_combination(self):
        return f'{self.address_line_1}, {self.city}, {self.state} {self.zip_code}'

    def get_avg_wait_time(self):
        return self.stops.aggregate(
            wait_time_avg=Avg(
                ExpressionWrapper(
                    F('departure_time') - F('arrival_time'),
                    output_field=DurationField(),
                ),
            ),
        )['wait_time_avg']


class LocationContact(GenericModel):
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='location_contacts',
        related_query_name='location_contact',
    )
    name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(
        max_length=19,
        blank=True,
        validators=[PhoneValidator()],
    )

    class Meta:
        db_table = 'location_contact'
        db_table_comment = 'Stores location contact information related to location.'

    def __str__(self):
        return textwrap.wrap(self.name, 50)[0]

    def get_absolute_url(self):
        return reverse('locations:location-contacts-detail', kwargs={'pk': self.pk})


class CommentType(GenericModel):
    status = ChoiceField(
        choices=PrimaryStatusChoices,
        default=PrimaryStatusChoices.ACTIVE,
    )
    severity = models.CharField(
        max_length=50,
        choices=[('H', 'High'), ('M', 'Medium'), ('L', 'Low')],
        default='L',
    )
    name = models.CharField(max_length=10)
    description = models.TextField()

    class Meta:
        ordering = ('organization',)
        db_table = 'comment_type'
        db_table_comment = 'Stores different types of comments.'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'organization',
                name='unique_comment_type_name_organization',
            ),
        ]

    def __str__(self):
        return textwrap.shorten(
            f'{self.name} - {self.description}',
            50,
            placeholder='...',
        )

    def clean(self):
        standard_codes = ['Dispatch', 'Billing', 'Hot']

        if self.name in standard_codes and self.status == PrimaryStatusChoices.INACTIVE:
            raise ValidationError(
                {
                    'status': 'The status of the standard comment '
                    'types cannot be set to inactive.',
                },
                code='invalid',
            )

    def get_absolute_url(self):
        return reverse('locations:comment-types-detail', kwargs={'pk': self.pk})


class LocationComment(GenericModel):
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='location_comments',
        related_query_name='location_comment',
    )
    comment_type = models.ForeignKey(
        CommentType,
        on_delete=models.PROTECT,
        related_name='location_comments',
        related_query_name='location_comment',
    )
    comment = models.TextField()
    entered_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='location_comments',
        related_query_name='location_comment',
    )

    class Meta:
        db_table = 'location_comment'
        ordering = ('location',)

    def __str__(self):
        return textwrap.shorten(
            f'{self.comment_type.name}: {self.comment}',
            width=50,
            placeholder='...',
        )

    def get_absolute_url(self):
        return reverse('locations:location-comments-detail', kwargs={'pk': self.pk})


class States(TimeStampedModel):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=5)
    country_name = models.CharField(max_length=255)
    country_iso3 = models.CharField(max_length=3)

    class Meta:
        ordering = ('name',)
        db_table = 'states'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'abbreviation',
                name='unique_name_abbreviation_state',
            ),
        ]

    def __str__(self):
        return textwrap.shorten(
            f'{self.name} - {self.abbreviation}',
            width=50,
            placeholder='...',
        )

    def get_absolute_url(self):
        return reverse('locations:states-detail', kwargs={'pk': self.pk})
