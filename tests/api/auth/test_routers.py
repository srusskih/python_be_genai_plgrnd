from typing import TYPE_CHECKING

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy import select

from api.auth.dependencies import get_auth_manager, get_current_user
from api.auth.managers import AuthManagerABC

if TYPE_CHECKING:
    from api.users.models import User


@pytest.mark.integration
def make_fake_auth_manager(
    user: "User", expected_password: str
) -> AuthManagerABC:
    """Create a fake auth manager for testing."""

    class FakeAuthManager(AuthManagerABC):
        """Fake AuthManager."""

        async def authenticate_user(self, email: str, password: str):
            """Mock authenticate user."""
            if email != user.email or password != expected_password:
                return None

            token = f"{email}:{password}"
            return user, token

    return FakeAuthManager()


@pytest.mark.integration
async def test_auth_sign_in(
    api_client: AsyncClient,
    dependencies_override_ctx,
    user_fixture,
    faker,
):
    """Test sign in endpoint."""
    user = user_fixture
    passwd = faker.isbn10()

    with dependencies_override_ctx(
        {
            get_auth_manager: lambda: make_fake_auth_manager(
                user,
                expected_password=passwd,
            ),
        }
    ):
        response = await api_client.post(
            "api/auth/sign_in",
            json={
                "user": {
                    "email": user.email,
                    "password": passwd,
                }
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "email": user.email,
        "authentication_token": f"{user.email}:{passwd}",
    }


@pytest.mark.integration
async def test_auth_sign_in_invalid(
    api_client: AsyncClient,
    dependencies_override_ctx,
    user_fixture,
    faker,
):
    """Test sign in endpoint with invalid credentials."""
    user = user_fixture
    passwd = faker.isbn10()

    with dependencies_override_ctx(
        {
            get_auth_manager: lambda: make_fake_auth_manager(
                user,
                expected_password=passwd,
            ),
        }
    ):
        response = await api_client.post(
            "api/auth/sign_in",
            json={
                "user": {
                    "email": user.email,
                    "password": "wrong_password",
                }
            },
        )

    assert response.status_code == 401


@pytest.mark.integration
async def test_auth_sign_out(
    db_session,
    api_client: AsyncClient,
    dependencies_override_ctx,
    user_fixture,
    faker,
):
    """Test sign out endpoint."""
    user = user_fixture
    authentication_token = faker.uuid4()

    with dependencies_override_ctx(
        {
            get_current_user: lambda: user,
        }
    ):
        response = await api_client.request(
            "DELETE",
            "/api/auth/sign_out",
            headers={"Authorization": f"Bearer {authentication_token}"},
            json={"user": {"email": user.email}},
        )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed out successfully."}

    # validate token is in denylist
    from api.users.models import JwtDenylist

    query = select(JwtDenylist).filter(JwtDenylist.jti == authentication_token)
    result = await db_session.execute(query)
    res = result.scalars().all()
    assert len(res) == 1


def raise_http_exception():
    """Raise HTTPException."""
    raise HTTPException(status_code=401)


@pytest.mark.integration
async def test_auth_sign_out_invalid_token(
    api_client: AsyncClient,
    dependencies_override_ctx,
    user_fixture,
):
    """Test sign out endpoint with invalid auth token."""
    user = user_fixture
    invalid_token = "invalid.token.value"
    headers = {"Authorization": f"Bearer {invalid_token}"}

    with dependencies_override_ctx(
        {
            get_current_user: raise_http_exception,
        }
    ):
        response = await api_client.request(
            "DELETE",
            "/api/auth/sign_out",
            json={"user": {"email": user.email}},
            headers=headers,
        )

    assert response.status_code in (401, 403)
