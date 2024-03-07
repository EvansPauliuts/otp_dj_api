import uuid

from django.db import models
from django.urls import reverse
from django.db.models.functions import Lower

from .business import BusinessUnit
from .organization import Organization


class Depot(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name='depots',
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='depots',
        related_query_name='depot',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)

    class Meta:
        db_table = 'depot'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'organization',
                name='unique_depot_name_organization',
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'accounts:organization-depot-detail',
            kwargs={'pk': self.pk},
        )


class Department(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name='departments',
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments',
        related_query_name='department',
    )
    depot = models.ForeignKey(
        Depot,
        on_delete=models.CASCADE,
        related_name='departments',
        related_query_name='department',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'department'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'accounts:organization-department-detail',
            kwargs={'pk': self},
        )
