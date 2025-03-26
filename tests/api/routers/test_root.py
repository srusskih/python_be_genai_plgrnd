"""Test the root endpoint."""


async def test_root(api_client):
	"""Test the homepage accessability."""
	response = api_client.get("/")
	assert response.status_code == 200
	assert response.json() == {"message": "Hello World"}
