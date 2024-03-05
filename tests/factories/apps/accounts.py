import secrets

import factory

from apps.accounts.models import BusinessUnit
from apps.accounts.models import JobTitle
from apps.accounts.models import Organization
from apps.accounts.models import Token
from apps.accounts.models import UserA
from apps.accounts.models import UserProfile


class BusinessUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BusinessUnit

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        business_unit, created = BusinessUnit.objects.get_or_create(
            name='TEST',
        )
        return business_unit


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        business_unit, b_created = BusinessUnit.objects.get_or_create(
            name='TEST',
        )
        organization, o_created = Organization.objects.get_or_create(
            name='Random Company',
            scac_code='TEST',
            business_unit=business_unit,
        )
        return organization


class JobTitleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobTitle

    business_unit = factory.SubFactory(BusinessUnitFactory)
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Faker('pystr', max_chars=100)
    description = factory.Faker('text')
    job_function = 'SYS_ADMIN'


class UserAFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserA

    username = 'test_user'
    email = 'test_user@test.com'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        business_unit, b_created = BusinessUnit.objects.get_or_create(
            name='TEST',
        )
        organization, o_created = Organization.objects.get_or_create(
            name='Random Company',
            scac_code='TEST',
            business_unit=business_unit,
        )

        user, created = UserA.objects.get_or_create(
            username=kwargs['username'],
            password='<PASSWORD>',
            email=kwargs['email'],
            is_staff=True,
            is_superuser=True,
            business_unit=business_unit,
            organization=organization,
        )
        return user


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    business_unit = factory.SubFactory(BusinessUnitFactory)
    organization = factory.SubFactory(OrganizationFactory)
    user = factory.SubFactory(UserAFactory)
    job_title = factory.SubFactory(JobTitleFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    address_line_1 = factory.Faker('street_address', locale='en_US')
    city = factory.Faker('city')
    state = 'NC'
    zip_code = factory.Faker('zipcode')


class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Token

    user = factory.SubFactory(UserAFactory)
    key = secrets.token_hex(20)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        token, created = Token.objects.get_or_create(
            user=kwargs['user'],
            key=kwargs['key'],
        )
        return token
