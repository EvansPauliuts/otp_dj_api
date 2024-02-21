import factory

from django.contrib.auth.models import User
from faker import Faker

from api.models import Token, User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'person{n}@example.com')
    phone = factory.Sequence(lambda n: f'+375 44 444-44-4{n}')
    password = factory.PostGenerationMethodCall(
        'set_password',
        'passer@@@111',
    )
    verified = 'True'
    firstname = fake.name()
    lastname = fake.name()


class SuperAdminUserFactory(UserFactory):
    verified = 'True'
    is_superuser = 'True'


class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Token

    token = fake.md5()
