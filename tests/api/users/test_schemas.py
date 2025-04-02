import pytest

from api.users.schemas import UserRegistration


def test_validate_password_confirmation():
    assert UserRegistration(
        email="test@example.com",
        password="password",
        password_confirmation="password",
    )


def test_should_raise_errors_when_passwords_do_not_match():
    with pytest.raises(ValueError):
        UserRegistration(
            email="test@example.com",
            password="password",
            password_confirmation="password1",
        )
