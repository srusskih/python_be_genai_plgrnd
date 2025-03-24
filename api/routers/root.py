"""Root router.
Contains the root endpoint.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def home():
    """Simple home page."""
    return {"message": "Hello World"}
