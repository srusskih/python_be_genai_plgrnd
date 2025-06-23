import pytest
from httpx import AsyncClient
from api.articles.models import Like


@pytest.mark.integration
async def test_article_likes_dislikes_in_response(
    api_client: AsyncClient, db_session
):
    # Create an article
    payload = {
        "article": {
            "title": "Like Test",
            "short_description": "desc",
            "description": "desc",
        }
    }
    create_resp = await api_client.post("/api/articles", json=payload)
    assert create_resp.status_code == 200
    article_id = create_resp.json()["id"]

    # Add Like record for this article
    like = Like(
        likeable_type="Article", likeable_id=article_id, likes=5, dislikes=2
    )
    db_session.add(like)
    await db_session.commit()

    # Check get by id
    get_resp = await api_client.get(f"/api/articles/{article_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["article_likes"] == 5
    assert data["article_dislikes"] == 2

    # Check list endpoint
    list_resp = await api_client.get("/api/articles")
    assert list_resp.status_code == 200
    articles = list_resp.json()
    found = next((a for a in articles if a["id"] == article_id), None)
    assert found is not None
    assert found["article_likes"] == 5
    assert found["article_dislikes"] == 2


@pytest.mark.integration
async def test_article_likes_dislikes_default_zero(api_client: AsyncClient):
    # Create an article without Like record
    payload = {
        "article": {
            "title": "No Like Record",
            "short_description": "desc",
            "description": "desc",
        }
    }
    create_resp = await api_client.post("/api/articles", json=payload)
    assert create_resp.status_code == 200
    article_id = create_resp.json()["id"]

    # Check get by id
    get_resp = await api_client.get(f"/api/articles/{article_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["article_likes"] == 0
    assert data["article_dislikes"] == 0

    # Check list endpoint
    list_resp = await api_client.get("/api/articles")
    assert list_resp.status_code == 200
    articles = list_resp.json()
    found = next((a for a in articles if a["id"] == article_id), None)
    assert found is not None
    assert found["article_likes"] == 0
    assert found["article_dislikes"] == 0
