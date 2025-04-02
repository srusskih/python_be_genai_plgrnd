import pytest

from api.users.managers import PasswordManager, UserAlreadyExists, UserManager

password_manager = PasswordManager(salt="a" * 16)


def test_should_generate_same_hash_for_same_password():
    assert password_manager.hash_password(
        "password"
    ) == password_manager.hash_password("password"), (
        "Password should be hashed the same way."
    )


def test_different_hashes_for_different_passwords():
    assert password_manager.hash_password(
        "password"
    ) != password_manager.hash_password("password1"), (
        "Should generate different hashes for different passwords."
    )


def test_should_verify_password():
    assert password_manager.verify_password(
        "password", password_manager.hash_password("password")
    ), "Password should be verified correctly."


def test_should_detect_invalid_password():
    assert not password_manager.verify_password(
        "password1", password_manager.hash_password("password")
    ), "Password should be invalid."


@pytest.mark.integration
async def test_should_create_user_without_passwords(db_session):
    user_manager = UserManager(db_session, password_manager)

    user = await user_manager.create_user("test@example.com")

    assert user.id is None
    assert user.email == "test@example.com"
    assert user.encrypted_password == "", "Password should be empty."


@pytest.mark.integration
async def test_should_create_user_with_passwords(db_session):
    user_manager = UserManager(db_session, password_manager)

    user = await user_manager.create_user("test@example.com", "123456")

    assert user.id is None
    assert user.email == "test@example.com"
    assert user.encrypted_password, "Password should not be empty."
    assert password_manager.verify_password(
        "123456", user.encrypted_password
    ), "Password should be verified correctly."


@pytest.mark.integration
async def test_should_raise_error_same_email_user_creation(db_session):
    user_manager = UserManager(db_session, password_manager)

    await user_manager.create_user("test@example.com", commit=True)

    with pytest.raises(UserAlreadyExists):
        await user_manager.create_user("test@example.com", commit=True)
