from unittest.mock import AsyncMock, MagicMock

import pytest

from api.auth.jwt import generate_jwt
from api.auth.managers import AuthManager
from api.users.managers import UserManager


@pytest.fixture
def mock_user_manager():
    def _factory(get_user_by_email, verify_password=None):
        mock = MagicMock(spec=UserManager)
        mock.get_user_by_email = AsyncMock()
        mock.verify_password = MagicMock()

        mock.get_user_by_email.return_value = get_user_by_email
        if verify_password is not None:
            mock.verify_password.return_value = verify_password
        return mock

    return _factory


async def test_authenticate_user_success(mock_user_manager, user_fixture):
    user_fixture.encrypted_password = "hashed_password"
    mock_manager = mock_user_manager(
        get_user_by_email=user_fixture, verify_password=True
    )
    auth_manager = AuthManager(user_manager=mock_manager)

    result = await auth_manager.authenticate_user(
        user_fixture.email, "password"
    )

    assert result is not None
    user, token = result
    assert user == user_fixture
    assert token == auth_manager.create_auth_token(user_fixture)

    mock_manager.get_user_by_email.assert_called_once_with(
        email=user_fixture.email
    )
    mock_manager.verify_password.assert_called_once_with(
        plain_password="password", hashed_password="hashed_password"
    )


async def test_authenticate_user_user_not_found(mock_user_manager):
    mock_manager = mock_user_manager(get_user_by_email=None)
    auth_manager = AuthManager(user_manager=mock_manager)

    result = await auth_manager.authenticate_user(
        "test@example.com", "password"
    )

    assert result is None
    mock_manager.get_user_by_email.assert_called_once_with(
        email="test@example.com"
    )


async def test_authenticate_user_invalid_password(
    mock_user_manager, user_fixture
):
    user_fixture.encrypted_password = "hashed_password"
    mock_manager = mock_user_manager(
        get_user_by_email=user_fixture, verify_password=False
    )
    auth_manager = AuthManager(user_manager=mock_manager)

    result = await auth_manager.authenticate_user(
        user_fixture.email, "wrong_password"
    )

    assert result is None
    mock_manager.get_user_by_email.assert_called_once_with(
        email=user_fixture.email
    )
    mock_manager.verify_password.assert_called_once_with(
        plain_password="wrong_password", hashed_password="hashed_password"
    )


@pytest.mark.integration
async def test_authenticate_user_by_token(db_session, faker):
    user_manager = UserManager(db_session, password_manager=MagicMock())
    auth_manager = AuthManager(user_manager=user_manager)

    created_user = await user_manager.create_user(user_email=faker.email())
    token = auth_manager.create_auth_token(created_user)

    result = await auth_manager.authenticate_user_by_token(token)
    assert result is not None

    auth_user, same_token = result
    assert auth_user.id == created_user.id
    assert same_token == token


@pytest.mark.integration
async def test_authenticate_user_by_token_invalid_token(db_session, faker):
    user_manager = UserManager(db_session, password_manager=MagicMock())
    auth_manager = AuthManager(user_manager=user_manager)

    created_user = await user_manager.create_user(user_email=faker.email())
    # Create a fake JWT token that is invalid (e.g., malformed or signed with wrong key)
    token = generate_jwt(
        {
            "sub": "me",
            "email": created_user.email,
            "auth": "test_server",
        },
        "some-secret",
        3600,
    )

    result = await auth_manager.authenticate_user_by_token(token)
    assert result is None


@pytest.mark.integration
async def test_authenticate_user_by_token_when_user_not_exists(
    db_session, user_fixture
):
    user_manager = UserManager(db_session, password_manager=MagicMock())
    auth_manager = AuthManager(user_manager=user_manager)

    token = auth_manager.create_auth_token(user_fixture)
    result = await auth_manager.authenticate_user_by_token(token)
    assert result is None


@pytest.mark.integration
async def test_authenticate_user_by_token_when_token_revoked(db_session, faker):
    user_manager = UserManager(db_session, password_manager=MagicMock())
    auth_manager = AuthManager(user_manager=user_manager)

    created_user = await user_manager.create_user(user_email=faker.email())

    token = auth_manager.create_auth_token(created_user)
    revoked_token = await auth_manager.sign_out(token)

    result = await auth_manager.authenticate_user_by_token(revoked_token)
    assert result is None
