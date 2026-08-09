def test_openapi_schema_is_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    body = response.json()

    assert body["info"]["title"] == "NEXUS OS"
    assert body["info"]["version"] == "0.1.0"
    assert "/api/v1/users/login" in body["paths"]
    assert "/api/v1/users/me" in body["paths"]


def test_swagger_docs_are_available(client):
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower()


def test_redoc_is_available(client):
    response = client.get("/redoc")

    assert response.status_code == 200
    assert "redoc" in response.text.lower()
