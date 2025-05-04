"""Root router.
Contains the root endpoint.
"""

from fastapi import APIRouter

from api.auth.routers import router as auth_router
from api.users.routers import router as user_router

router = APIRouter()
router.include_router(user_router, prefix="/users")
router.include_router(auth_router, prefix="/api/auth")


@router.get("/")
async def home():
    """Simple home page."""
    return {"message": "Hello World"}
