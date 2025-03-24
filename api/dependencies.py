"""Fast API Application for API Application.

Usage example:

```python
# some_router.py
from api.settings import Settings
from api.dependencies import get_settings


@router.get("/some-endpoint")
async def some_endpoint(
    settings: Annotate[Settings, Depends(get_settings)],
): ...
```
"""
