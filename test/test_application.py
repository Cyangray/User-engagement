from fastapi.testclient import TestClient

from src.application import app


def test_startup():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "Hello, I'm good!"
