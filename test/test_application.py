from fastapi.testclient import TestClient
from pydantic import ValidationError
from src.application import app, User, SuperUser, Activity
import pytest
from datetime import datetime, timezone

mock_data_user = {
    "user_id": 1,
    "username": "Pippo",
    "email": "aaa@bbb.cc",
    "age": 23,
    "country": "UK",
}

mock_data_superuser = {
    "user_id": 1,
    "username": "Pippo",
    "email": "aaa@bbb.cc",
    "age": 23,
    "country": "UK",
    "superuser_id": 1,
    "role": "moderator",
}

mock_data_activity = {
    "activity_id": 1,
    "time": datetime(2024, 10, 23, 9, 41, 3, tzinfo=timezone.utc),
    "user_id": 3,
    "activity_type": "login",
    "activity_details": "First login of the day",
}


def test_startup():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "Hello, I'm good!"


def test_valid_user():
    assert User(**mock_data_user).model_dump() == mock_data_user


def test_valid_superuser():
    assert SuperUser(**mock_data_superuser).model_dump() == mock_data_superuser


def test_valid_activity():
    assert Activity(**mock_data_activity).model_dump() == mock_data_activity


def test_invalid_user_data():
    user = User(**mock_data_user)

    with pytest.raises(ValidationError):
        user.user_id = -1
    with pytest.raises(ValidationError):
        user.username = 12
    with pytest.raises(ValidationError):
        user.username = "Pippo333"
    with pytest.raises(ValidationError):
        user.email = "sssss"
    with pytest.raises(ValidationError):
        user.age = "ii"
    with pytest.raises(ValidationError):
        user.age = -22
    with pytest.raises(ValidationError):
        user.country = "UKee"


def test_invalid_activity():
    activity = Activity(**mock_data_activity)
    with pytest.raises(ValidationError):
        activity.activity_id = -1
    with pytest.raises(ValidationError):
        activity.time = -3
    with pytest.raises(ValidationError):
        activity.time = "Pippo"
    with pytest.raises(ValidationError):
        activity.user_id = -1
    with pytest.raises(ValidationError):
        activity.activity_type = "Login"
    with pytest.raises(ValidationError):
        activity.activity_type = "Pippo"
    with pytest.raises(ValidationError):
        activity.activity_type = ""
    with pytest.raises(ValidationError):
        activity.activity_details = 33


def test_invalid_superuser_data():
    superuser = SuperUser(**mock_data_superuser)
    with pytest.raises(ValidationError):
        superuser.superuser_id = -1
    with pytest.raises(ValidationError):
        superuser.role = "Admin"
    with pytest.raises(ValidationError):
        superuser.role = "Pippo"
    with pytest.raises(ValidationError):
        superuser.role = ""
    with pytest.raises(ValidationError):
        superuser.role = 33
