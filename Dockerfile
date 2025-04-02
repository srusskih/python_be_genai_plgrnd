FROM python:3.12-alpine
COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

ADD . /app
WORKDIR /app
RUN uv sync --frozen

# Run the FastAPI application with uvicorn
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]