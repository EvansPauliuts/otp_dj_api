import re

from django.core.management import BaseCommand
from django.db import transaction

from apps.accounts.models import JobTitle
from apps.accounts.models import Organization
from apps.accounts.models import UserA
from apps.accounts.models import UserProfile
from core.utils.helpers import get_or_create_business_unit


class Command(BaseCommand):
    help = 'Creates system user account and organization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the system user account',
            default='dev',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the system user account',
            default='system@dev.app',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the system user account',
            required=True,
        )
        parser.add_argument(
            '--organization',
            type=str,
            help='Name of system organization.',
            default='system',
        )
        parser.add_argument(
            '--business_unit',
            type=str,
            help='Name of the system business unit.',
            default='bussiness',
        )

    @staticmethod
    def create_system_organization(organization_name, bs_unit):
        organization, created = Organization.objects.get_or_create(
            name=organization_name,
            business_unit=bs_unit,
            defaults={
                'scac_code': organization_name[:4],
            },
        )
        return organization

    @staticmethod
    def create_system_job_title(organization, bs_unit):
        job_title, created = JobTitle.objects.get_or_create(
            organization=organization,
            name='System',
            business_unit=bs_unit,
            defaults={'description': 'System job title.'},
            job_function=JobTitle.JobFunctionChoices.SYS_ADMIN,
        )
        return job_title

    @transaction.atomic(using='default')
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        organization_name = options['organization']
        bs_unit_name = options['business_unit']

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            self.stderr.write(self.style.ERROR('Invalid email address'))
            return

        if not re.match(r'^[a-zA-Z0-9 ]+$', username):
            self.stderr.write(self.style.ERROR('Invalid username'))
            return

        business_unit = get_or_create_business_unit(bs_name=bs_unit_name)
        organization = self.create_system_organization(organization_name, business_unit)
        job_title = self.create_system_job_title(organization, business_unit)

        if UserA.objects.filter(username=username).exists():
            self.stderr.write(self.style.ERROR(f'User {username} already exists'))
            return

        user = UserA.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            organization=organization,
            business_unit=business_unit,
        )

        UserProfile.objects.get_or_create(
            organization=organization,
            business_unit=business_unit,
            user=user,
            job_title=job_title,
            defaults={
                'first_name': 'System',
                'last_name': 'User',
                'address_line_1': '1234 Main St.',
                'city': 'Anytown',
                'state': 'NY',
                'zip_code': '12345',
                'phone_number': '123-456-7890',
            },
        )

        self.stdout.write(
            self.style.SUCCESS('System user account created. Successfully')
        )
