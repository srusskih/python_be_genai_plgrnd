FROM python:3.12-alpine
COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

ADD . /app
WORKDIR /app
RUN uv sync --frozen

ENV API_APP_PORT=3002

# Expose the API port
EXPOSE ${API_APP_PORT}

# Run the FastAPI application with uvicorn
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "${API_APP_PORT}}"]