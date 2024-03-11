import random
import string

from django.db import transaction
from rich.progress import Progress
from core.utils.helpers import get_or_create_business_unit
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User, JobTitle, UserProfile, Organization

class Command(BaseCommand):
    help = 'Create test users.'

    @transaction.atomic
    def handle(self, *args, **options):
        business_unit = get_or_create_business_unit(bs_name='Transportation')

        system_org_answer = input(
            "What is the SCAC of organization you'd like to add the test users to? (Scac Code) ",
        )
        number_of_users_answer = input('How many test users would you like to create? ')

        try:
            system_org = Organization.objects.get(scac_code=system_org_answer)
        except Organization.DoesNotExist as e:
            raise CommandError(
                f'Organization {system_org_answer} does not exist.',
            ) from e

        try:
            number_of_users = int(number_of_users_answer)
        except ValueError as e:
            raise CommandError(
                f'{number_of_users_answer} is not a valid number.',
            ) from e

        job_title, _ = JobTitle.objects.get_or_create(
            name='Test User',
            organization=system_org,
            business_unit=business_unit,
            job_function=JobTitle.JobFunctionChoices.TEST,
        )

        usernames = [f'testuser-{i}' for i in range(number_of_users)]
        existing_users = User.objects.filter(username__in=usernames).values_list(
            'username',
            flat=True,
        )

        new_users = []
        with Progress() as progress:
            task = progress.add_task(
                '[cyan]Creating test users...',
                total=number_of_users,
            )

            for i in range(number_of_users):
                if usernames[i] in existing_users:
                    progress.update(task, advance=1)
                    continue

                email = f'testuser-{i}@dev.app'
                password = 'testuser'.join(
                    random.choices(string.ascii_uppercase + string.digits, k=8),
                )

                new_user = User(
                    username=usernames[i],
                    email=email,
                    password=password,
                    organization=system_org,
                    business_unit=business_unit,
                )
                new_users.append(new_user)
                progress.update(task, advance=1)

        User.objects.bulk_create(new_users)

        new_profiles = []

        with Progress() as progress:
            task = progress.add_task(
                '[cyan]Creating user profiles...',
                total=number_of_users,
            )

            for i in range(number_of_users):
                if usernames[i] in existing_users:
                    progress.update(task, advance=1)
                    continue

                user = User.objects.get(username=usernames[i])
                new_profile = UserProfile(
                    user=user,
                    organization=system_org,
                    business_unit=business_unit,
                    job_title=job_title,
                    first_name='Test',
                    last_name=f'User-{i}',
                    address_line_1='123 Test Street',
                    city='Test City',
                    state='CA',
                    zip_code='12345',
                    phone_number='+375 (44) 444-44-44',
                )
                new_profiles.append(new_profile)
                progress.update(task, advance=1)

        UserProfile.objects.bulk_create(new_profiles)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {number_of_users} test users.'),
        )
