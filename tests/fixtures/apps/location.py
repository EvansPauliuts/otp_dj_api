import pytest

from tests.factories.apps.location import CommentTypeFactory
from tests.factories.apps.location import LocationCategoryFactory
from tests.factories.apps.location import LocationContactFactory
from tests.factories.apps.location import LocationFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def location():
    yield LocationFactory()


@pytest.fixture
def location_category():
    yield LocationCategoryFactory()


@pytest.fixture
def comment_type():
    yield CommentTypeFactory()


@pytest.fixture
def location_contact():
    yield LocationContactFactory()
