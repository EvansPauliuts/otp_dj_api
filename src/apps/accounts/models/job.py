import uuid

from core.models import ChoiceField
from core.models import GenericModel
from core.models import PrimaryStatusChoices
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse


class JobTitle(GenericModel):
    class JobFunctionChoices(models.TextChoices):
        MANAGER = 'MANAGER', 'Manager'
        MANAGEMENT_TRAINEE = 'MANAGEMENT_TRAINEE', 'Management Trainee'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'
        DISPATCHER = 'DISPATCHER', 'Dispatcher'
        BILLING = 'BILLING', 'Billing'
        FINANCE = 'FINANCE', 'Finance'
        SAFETY = 'SAFETY', 'Safety'
        SYS_ADMIN = 'SYS_ADMIN', 'System Administrator'
        TEST = 'TEST', 'Test Job Function'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    status = ChoiceField(
        choices=PrimaryStatusChoices,
        default=PrimaryStatusChoices.ACTIVE,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    job_function = ChoiceField(choices=JobFunctionChoices)

    class Meta:
        db_table = 'job_title'
        db_table_comment = 'Stores the job title information related to users.'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'organization',
                name='unique_job_title_organization',
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'accounts:job_titles-detail',
            kwargs={'pk': self.pk},
        )
