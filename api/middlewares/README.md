# APi Middlewares

Place to write custom middlewares for the API Application

Expected usage example:

```python
# app.py

# ...
from api.middlewares import CustomMiddleware
# ...

def create_app(...):
    app = FastAPI(...)
    # ...
    app.add_middleware(CustomMiddleware, ...)
    # ...
    return app
```
