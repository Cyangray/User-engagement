from fastapi.testclient import TestClient

from src.application import app, users_id_db

client = TestClient(app)


def test_startup():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, I'm good!"


def test_post_user(mock_data_user):
    response = client.post(
        "/users/",
        params=mock_data_user,
    )
    data = response.json()
    assert "user_id" in data
    excluded_keys = ["user_id"]
    for key, value in mock_data_user.items():
        if key not in excluded_keys:
            assert data[key] == value
    assert response.status_code == 200


def test_post_superuser(mock_data_superuser_complete):
    response = client.post("/superusers/", params=mock_data_superuser_complete)
    data = response.json()
    assert data == mock_data_superuser_complete
    assert response.status_code == 200


def test_post_activity(mock_data_activity):
    users_id_db.append(mock_data_activity["user_id"])
    response = client.post("/activities/", params=mock_data_activity)
    data = response.json()
    assert "activity_id" in data
    excluded_keys = ["activity_id"]
    for key, value in mock_data_activity.items():
        if key not in excluded_keys:
            assert data[key] == value
    assert response.status_code == 200


def test_filter_activities_by_user_id(mock_data_user, mock_data_activity):
    users_id_db.append(mock_data_activity["user_id"])
    client.post("/activities/", json=mock_data_activity)
    response = client.get(f"/activities/?user_id={mock_data_user["user_id"]}")
    data = response.json()
    excluded_keys = ["activity_id"]
    for key, value in mock_data_activity.items():
        if key not in excluded_keys:
            assert data[0][key] == value
    assert response.status_code == 200


def test_fail_filter_activities_user_id_not_found(mock_data_user, mock_data_activity):
    client.post("/activities/", json=mock_data_activity)
    response = client.get(f"/activities/?user_id={mock_data_user["user_id"] + 1}")
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "User ID not found."
