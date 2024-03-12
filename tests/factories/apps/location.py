import factory
from apps.location.models import CommentType
from apps.location.models import Location
from apps.location.models import LocationCategory
from apps.location.models import LocationComment
from apps.location.models import LocationContact

from tests.factories.apps.accounts import BusinessUnitFactory
from tests.factories.apps.accounts import OrganizationFactory


class LocationCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LocationCategory

    business_unit = factory.SubFactory(BusinessUnitFactory)
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Faker('pystr', max_chars=100)


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    business_unit = factory.SubFactory(BusinessUnitFactory)
    organization = factory.SubFactory(OrganizationFactory)
    code = factory.Faker('pystr', max_chars=10)
    name = factory.Faker('pystr', max_chars=100)
    location_category = factory.SubFactory(LocationCategoryFactory)
    address_line_1 = factory.Faker('address', locale='en_US')
    city = factory.Faker('city', locale='en_US')
    state = 'NC'
    zip_code = factory.Faker('zipcode', locale='en_US')


class LocationContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LocationContact

    business_unit = factory.SubFactory(BusinessUnitFactory)
    organization = factory.SubFactory(OrganizationFactory)
    location = factory.SubFactory(LocationFactory)
    name = factory.Faker('pystr', max_chars=100)
    email = factory.Faker('email', locale='en_US')


class CommentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentType

    business_unit = factory.SubFactory(BusinessUnitFactory)
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Faker('text', locale='en_US', max_nb_chars=10)
    description = factory.Faker('text', locale='en_US', max_nb_chars=10)


class LocationCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LocationComment

    business_unit = factory.SubFactory(BusinessUnitFactory)
    organization = factory.SubFactory(OrganizationFactory)
    location = factory.SubFactory(LocationFactory)
    comment_type = factory.SubFactory(CommentTypeFactory)
    comment = factory.Faker('text', locale='en_US')
    entered_by = factory.SubFactory('accounts.UserFactory')
