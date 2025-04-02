"""Root router.
Contains the root endpoint.
"""

from fastapi import APIRouter

from api.users.routers import router as user_router

router = APIRouter()
router.include_router(user_router)


@router.get("/")
async def home():
    """Simple home page."""
    return {"message": "Hello World"}
