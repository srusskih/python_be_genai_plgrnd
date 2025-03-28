"""API Settings."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class CorsSettings(BaseModel):
    """CORS Middleware Settings."""

    allow_origins: list[str] = ["*"]
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    allow_credentials: bool = True


class Settings(BaseSettings):
    """API Settings."""

    model_config = SettingsConfigDict(
        env_prefix="API_",
        # no need to provide full nested object
        nested_model_default_partial_update=True,
        # "A__B__C" -> A.B.C
        env_nested_delimiter="__",
    )

    DEBUG: bool = True
    APP_PORT: int = 3000
    VERSION: str = "0.0.1"

    CORS_MIDDLEWARE: CorsSettings = CorsSettings()
