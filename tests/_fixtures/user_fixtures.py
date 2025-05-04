import faker
import pytest

from api.users.models import User

__all__ = [
    "user_fixture",
]


@pytest.fixture
def user_fixture(faker: faker.Faker) -> User:
    """Create a user fixture."""
    return User(
        id=faker.pyint(),
        email=faker.email(),
        encrypted_password="",
    )
