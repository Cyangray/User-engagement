from fastapi.testclient import TestClient

from src.application import app
from test.conftest import (
    mock_data_user,
    mock_data_activity,
    mock_data_superuser_complete,
)

client = TestClient(app)


def test_startup():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, I'm good!"


def test_post_user():
    response = client.post(
        "/users/",
        json=mock_data_user,
    )
    data = response.json()
    assert "user_id" in data
    assert data["email"] == mock_data_user["email"]
    assert data["username"] == mock_data_user["username"]
    assert data["age"] == mock_data_user["age"]
    assert data["country"] == mock_data_user["country"]
    assert response.status_code == 200


def test_post_superuser():
    response = client.post("/superusers/", json=mock_data_superuser_complete)
    data = response.json()
    assert "superuser_id" in data
    assert data["user_id"] == mock_data_superuser_complete["user_id"]
    assert data["email"] == mock_data_superuser_complete["email"]
    assert data["username"] == mock_data_superuser_complete["username"]
    assert data["age"] == mock_data_superuser_complete["age"]
    assert data["country"] == mock_data_superuser_complete["country"]
    assert data["role"] == mock_data_superuser_complete["role"]
    assert response.status_code == 200


def test_post_activity():
    response = client.post("/activities/", json=mock_data_activity)
    data = response.json()
    assert "activity_id" in data
    assert "time" in data
    assert data["user_id"] == mock_data_activity["user_id"]
    assert data["activity_type"] == mock_data_activity["activity_type"]
    assert data["activity_details"] == mock_data_activity["activity_details"]
    assert response.status_code == 200


def test_filter_activities_by_user_id():
    client.post("/users/", json=mock_data_user)
    client.post("/activities/", json=mock_data_activity)
    response = client.get(f"/activities/?user_id={mock_data_user["user_id"]}")
    data = response.json()
    assert data[0]["activity_id"] == mock_data_activity["activity_id"]
    assert data[0]["user_id"] == mock_data_activity["user_id"]
    assert data[0]["activity_type"] == mock_data_activity["activity_type"]
    assert data[0]["activity_details"] == mock_data_activity["activity_details"]
    assert response.status_code == 200


def test_fail_filter_activities_user_id_not_found():
    client.post("/users/", json=mock_data_user)
    client.post("/activities/", json=mock_data_activity)
    response = client.get(f"/activities/?user_id={mock_data_user["user_id"] + 1}")
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "User ID not found."
