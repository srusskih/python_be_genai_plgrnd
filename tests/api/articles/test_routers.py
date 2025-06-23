import pytest
from httpx import AsyncClient

from api.articles.models import Article


@pytest.mark.integration
async def test_create_article(api_client: AsyncClient, db_session):
    payload = {
        "article": {
            "title": "Test Article",
            "short_description": "Short desc",
            "description": "Full article text",
        }
    }
    response = await api_client.post("/api/articles", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == payload["article"]["title"]
    assert data["short_description"] == payload["article"]["short_description"]
    assert data["description"] == payload["article"]["description"]
    assert "created_at" in data
    assert "updated_at" in data

    # Check DB
    article = await db_session.get(Article, data["id"])
    assert article is not None
    assert article.title == payload["article"]["title"]
    assert article.short_description == payload["article"]["short_description"]
    assert article.description == payload["article"]["description"]


@pytest.mark.integration
async def test_get_article_by_id(api_client: AsyncClient):
    # Create an article first
    payload = {
        "article": {
            "title": "Get By ID",
            "short_description": "Desc",
            "description": "Text",
        }
    }
    create_resp = await api_client.post("/api/articles", json=payload)
    assert create_resp.status_code == 200
    article_id = create_resp.json()["id"]

    # Retrieve the article by ID
    get_resp = await api_client.get(f"/api/articles/{article_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == article_id
    assert data["title"] == payload["article"]["title"]
    assert data["short_description"] == payload["article"]["short_description"]
    assert data["description"] == payload["article"]["description"]
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.integration
async def test_get_article_by_id_not_found(api_client: AsyncClient):
    resp = await api_client.get("/api/articles/999999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Article not found"


@pytest.mark.integration
async def test_list_articles(api_client: AsyncClient):
    # Create two articles
    payload1 = {
        "article": {
            "title": "A1",
            "short_description": "S1",
            "description": "D1",
        }
    }
    payload2 = {
        "article": {
            "title": "A2",
            "short_description": "S2",
            "description": "D2",
        }
    }
    await api_client.post("/api/articles", json=payload1)
    await api_client.post("/api/articles", json=payload2)

    resp = await api_client.get("/api/articles")
    assert resp.status_code == 200
    articles = resp.json()
    assert isinstance(articles, list)
    assert any(a["title"] == "A1" for a in articles)
    assert any(a["title"] == "A2" for a in articles)


@pytest.mark.integration
async def test_update_article(api_client: AsyncClient, db_session):
    # Create an article
    payload = {
        "article": {
            "title": "Old Title",
            "short_description": "Old",
            "description": "Old",
        }
    }
    create_resp = await api_client.post("/api/articles", json=payload)
    article_id = create_resp.json()["id"]

    # Update it
    update_payload = {
        "article": {
            "title": "New Title",
            "short_description": "New",
            "description": "New",
        }
    }
    update_resp = await api_client.put(
        f"/api/articles/{article_id}", json=update_payload
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["id"] == article_id
    assert data["title"] == "New Title"
    assert data["short_description"] == "New"
    assert data["description"] == "New"

    # Check DB
    article = await db_session.get(Article, article_id)
    assert article.title == "New Title"
    assert article.short_description == "New"
    assert article.description == "New"


@pytest.mark.integration
async def test_update_article_not_found(api_client: AsyncClient):
    update_payload = {
        "article": {"title": "X", "short_description": "X", "description": "X"}
    }
    resp = await api_client.put("/api/articles/999999", json=update_payload)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Article not found"


@pytest.mark.integration
async def test_delete_article(api_client: AsyncClient):
    # Create an article
    payload = {
        "article": {
            "title": "To Delete",
            "short_description": "Del",
            "description": "Del",
        }
    }
    create_resp = await api_client.post("/api/articles", json=payload)
    article_id = create_resp.json()["id"]

    # Delete it
    delete_resp = await api_client.delete(f"/api/articles/{article_id}")
    assert delete_resp.status_code == 204
    # Ensure it's gone
    get_resp = await api_client.get(f"/api/articles/{article_id}")
    assert get_resp.status_code == 404


@pytest.mark.integration
async def test_delete_article_not_found(api_client: AsyncClient):
    resp = await api_client.delete("/api/articles/999999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Article not found"


@pytest.fixture
async def article_with_comments(db_session, api_client):
    """Creates an article and attaches two comments, returns article_id and
    comment contents.
    """
    payload = {
        "article": {
            "title": "Article with comments",
            "short_description": "desc",
            "description": "desc",
        }
    }
    create_resp = await api_client.post("/api/articles", json=payload)
    article_id = create_resp.json()["id"]
    from api.articles.models import Comment

    comment1 = Comment(article_id=article_id, content="First comment")
    comment2 = Comment(article_id=article_id, content="Second comment")
    db_session.add_all([comment1, comment2])
    await db_session.commit()
    return article_id, {"First comment", "Second comment"}


@pytest.mark.integration
async def test_article_get_by_id_includes_comments(
    api_client: AsyncClient, article_with_comments
):
    article_id, expected_comments = article_with_comments
    get_resp = await api_client.get(f"/api/articles/{article_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert "comments" in data
    assert isinstance(data["comments"], list)
    assert len(data["comments"]) == 2
    assert {c["content"] for c in data["comments"]} == expected_comments


@pytest.mark.integration
async def test_article_list_includes_comments(
    api_client: AsyncClient, article_with_comments
):
    article_id, expected_comments = article_with_comments
    list_resp = await api_client.get("/api/articles")
    assert list_resp.status_code == 200
    articles = list_resp.json()
    found = next((a for a in articles if a["id"] == article_id), None)
    assert found is not None
    assert "comments" in found
    assert len(found["comments"]) == 2
    assert {c["content"] for c in found["comments"]} == expected_comments
