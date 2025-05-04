import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from api.auth.dependencies import get_current_user
from api.auth.managers import AuthManager


@pytest.fixture
def mock_auth_manager_factory():
    def _factory(**kwargs):
        mock = AsyncMock(spec=AuthManager)
        for attr, value in kwargs.items():
            setattr(mock, attr, value)
        return mock

    return _factory


async def test_get_current_user_valid_token(mock_auth_manager_factory):
    mock_auth_manager = mock_auth_manager_factory(
        authenticate_user_by_token=AsyncMock(
            return_value=("mock_user", "mock_data")
        )
    )
    token = "valid_token"
    result = await get_current_user(token=token, auth_manager=mock_auth_manager)
    assert result == "mock_user"
    mock_auth_manager.authenticate_user_by_token.assert_called_once_with(
        token=token
    )


async def test_get_current_user_invalid_token(mock_auth_manager_factory):
    mock_auth_manager = mock_auth_manager_factory(
        authenticate_user_by_token=AsyncMock(return_value=None)
    )
    token = "invalid_token"
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token, auth_manager=mock_auth_manager)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"
    mock_auth_manager.authenticate_user_by_token.assert_called_once_with(
        token=token
    )
