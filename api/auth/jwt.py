from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import SecretStr

__all__ = [
    "generate_jwt",
    "decode_jwt",
    "InvalidTokenError",
    "SecretType",
    "JWT_ALGORITHM",
]

SecretType = Union[str, SecretStr]
JWT_ALGORITHM = "HS256"


def _get_secret_value(secret: SecretType) -> str:
    """
    Extracts the string value from a secret,
    whether it is a plain string or a Pydantic SecretStr.

    Args:
        secret (SecretType): The secret value as a string or SecretStr.

    Returns:
        str: The plain string value of the secret.
    """
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def generate_jwt(
    data: dict,
    secret: SecretType,
    lifetime_seconds: Optional[int] = None,
    algorithm: str = JWT_ALGORITHM,
) -> str:
    """
    Generates a JSON Web Token (JWT) from the provided data and secret.

    Args:
        data (dict): The payload data to encode in the JWT.
        secret (SecretType): The secret key used to sign the JWT.
        lifetime_seconds (Optional[int], optional): Token lifetime in seconds.
            If provided, sets the 'exp' claim. Defaults to None.
        algorithm (str, optional): The algorithm to use for encoding.
            Defaults to 'HS256'.

    Returns:
        str: The encoded JWT as a string.
    """
    payload = data.copy()
    if lifetime_seconds:
        expire = datetime.now(timezone.utc) + timedelta(
            seconds=lifetime_seconds
        )
        payload["exp"] = expire
    return jwt.encode(payload, _get_secret_value(secret), algorithm=algorithm)


def decode_jwt(
    encoded_jwt: str,
    secret: SecretType,
    audience: list[str],
    algorithms: list[str] | None = None,
) -> dict[str, Any]:
    """
    Decodes and verifies a JSON Web Token (JWT).

    Args:
        encoded_jwt (str): The JWT string to decode.
        secret (SecretType): The secret key used to verify the JWT.
        audience (list[str]): List of valid audiences for the token.
        algorithms (list[str], optional): List of acceptable algorithms.
            Defaults to ['HS256'].

    Returns:
        dict[str, Any]: The decoded JWT payload as a dictionary.
    """
    if algorithms is None:
        algorithms = [JWT_ALGORITHM]
    return jwt.decode(
        encoded_jwt,
        _get_secret_value(secret),
        audience=audience,
        algorithms=algorithms,
    )
