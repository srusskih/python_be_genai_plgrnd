from unittest import mock

import pytest
from sqlalchemy import select

from api.users.models import User


@pytest.mark.integration
async def test_should_register_new_user(api_client, db_session):
    # Act
    response = await api_client.post(
        "http://test/users",
        json={
            "registration": {
                "email": "test@example.com",
                "password": "password123",
                "password_confirmation": "password123",
            }
        },
    )

    # Assert that the response is successful
    assert response.status_code == 200
    assert response.json() == {
        "id": mock.ANY,
        "email": "test@example.com",
    }

    # Assert that the user was created in the database
    q = select(User).filter(User.id == response.json()["id"])
    created_user = (await db_session.execute(q)).scalar()
    assert created_user is not None
    assert created_user.email == "test@example.com"
    assert created_user.encrypted_password


@pytest.mark.integration
async def test_should_not_reg_new_user_in_case_of_invalid_params(
    api_client, db_session
):
    # Act
    response = await api_client.post(
        "http://test/users",
        json={
            "registration": {
                "email": "test@example.com",
                "password": "password123",
                "password_confirmation": "password1234",
            }
        },
    )

    # Assert that the response is successful
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "registration"]
    assert (
        response.json()["detail"][0]["msg"]
        == "Value error, Passwords do not match"
    )

    # Assert that the user was created in the database
    q = select(User).filter(User.email == "test@example.com")
    created_user = (await db_session.execute(q)).scalar()
    assert created_user is None


@pytest.mark.integration
async def test_should_not_reg_new_user_with_same_email(api_client):
    # Arrange
    # Create a user
    response = await api_client.post(
        "http://test/users",
        json={
            "registration": {
                "email": "test@example.com",
                "password": "password123",
                "password_confirmation": "password123",
            }
        },
    )
    assert response.status_code == 200

    # Act
    # Try to create a user with the same email
    response = await api_client.post(
        "http://test/users",
        json={
            "registration": {
                "email": "test@example.com",
                "password": "password123",
                "password_confirmation": "password123",
            }
        },
    )

    # Assert that the response is successful
    assert response.status_code == 409
    assert response.json() == {"detail": [{"msg": "User already exists."}]}
