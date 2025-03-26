"""General fixtures for tests."""

import pytest

from fastapi.testclient import TestClient

from api.app import create_app
from api.settings import Settings


@pytest.fixture
def api_client():
	""" "Create a test client."""
	settings = Settings()
	app = create_app(settings)

	return TestClient(app)
