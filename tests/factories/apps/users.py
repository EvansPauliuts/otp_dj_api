import factory
from apps.users.models import Token
from apps.users.models import User
from faker import Faker

fake = Faker()


def generate_username(*args, **kwargs):
    return fake.profile(fields=['firstname', 'lastname'])


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'person{n}@example.com')
    phone = factory.Sequence(lambda n: f'+375 44 444-44-4{n}')
    password = factory.PostGenerationMethodCall('set_password', 'hello@@@111')
    verified = 'True'
    firstname = fake.name()
    lastname = fake.name()
    username = factory.LazyAttribute(generate_username)


class SuperAdminUserFactory(UserFactory):
    verified = 'True'
    is_superuser = 'True'


class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Token

    token = fake.md5()
