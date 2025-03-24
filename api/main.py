"""API Application Runner."""

import uvicorn

from api.app import create_app
from api.settings import Settings

settings = Settings()
app = create_app(settings)

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True
    )
