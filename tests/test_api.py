from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_and_manifest():
    health = client.get("/health")
    manifest = client.get("/manus-routes.json")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert manifest.status_code == 200
    assert manifest.json()["routes"][0]["path"] == "/"


def test_homepage_contains_brief_form():
    response = client.get("/")
    assert response.status_code == 200
    assert "Generate my comic" in response.text
    assert 'name="story_prompt"' in response.text


def test_json_generation_contract():
    response = client.post(
        "/generate-comic/json",
        json={
            "story_prompt": "A brave fox discovers a door inside an ancient tree.",
            "character_name": "Moxie",
            "setting": "an enchanted forest",
            "tone": "Funny",
            "art_style": "Comic book",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["comic"]["panels"]) == 5
    assert data["comic"]["pdf_url"].endswith(".pdf")


def test_image_test_route():
    response = client.post("/test-image", json={"prompt": "a tiny moon bakery", "art_style": "Retro pulp"})
    assert response.status_code == 200
    assert response.json()["image_url"].startswith("/static/panels/")


def test_openapi_exposes_typed_json_contracts():
    schema = client.get("/openapi.json").json()
    assert "ComicResponse" in str(schema["paths"]["/generate-comic/json"]["post"])
    assert "ImageTestResponse" in str(schema["paths"]["/test-image"]["post"])
    assert "HealthResponse" in str(schema["paths"]["/health"]["get"])


def test_form_error_returns_recovery_state(monkeypatch):
    import app.routes as routes

    def fail(_payload):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(routes, "create_comic", fail)
    response = client.post("/generate", data={"story_prompt": "A brave fox finds a door.", "character_name": "Moxie", "setting": "the forest", "tone": "Funny", "art_style": "Comic book"})
    assert response.status_code == 500
    assert "The ink pass stalled" in response.text
