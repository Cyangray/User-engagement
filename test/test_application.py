from fastapi.testclient import TestClient
from pydantic import ValidationError
from src.application import app, User, SuperUser, Activity
import pytest
from datetime import datetime, timezone


def test_startup():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "Hello, I'm good!"


def test_valid_user():
    mock_data_user = {
        "user_id": 1,
        "username": "Pippo",
        "email": "aaa@bbb.cc",
        "age": 23,
        "country": "UK",
    }
    assert User(**mock_data_user).model_dump() == mock_data_user


def test_valid_superuser():
    mock_data_superuser = {
        "user_id": 1,
        "username": "Pippo",
        "email": "aaa@bbb.cc",
        "age": 23,
        "country": "UK",
        "superuser_id": 1,
        "role": "moderator",
    }
    assert SuperUser(**mock_data_superuser).model_dump() == mock_data_superuser


def test_valid_activity():
    mock_data_activity = {
        "activity_id": 1,
        "time": datetime(2024, 10, 23, 9, 41, 3, tzinfo=timezone.utc),
        "user_id": 3,
        "activity_type": "login",
        "activity_details": "First login of the day",
    }
    assert Activity(**mock_data_activity).model_dump() == mock_data_activity


def test_invalid_user_data():
    with pytest.raises(ValidationError):
        User(user_id=-1)
        User(user_id="1")
        User(username=12)
        User(username="Pippo333")
        User(email="sssss")
        User(age="ii")
        User(age=-22)
        User(country="UKee")


def test_invalid_superuser_data():
    with pytest.raises(ValidationError):
        SuperUser(superuser_id=-1)
        SuperUser(superuser_id="1")
        SuperUser(role="Admin")
        SuperUser(role="Pippo")
        SuperUser(role="")
        SuperUser(role=33)


def test_invalid_activity():
    with pytest.raises(ValidationError):
        Activity(activity_id=-1)
        Activity(activity_id="1")
        Activity(
            time=datetime(2024, 10, 23, 9, 41, 3, tzinfo=timezone.utc).isoformat(
                timespec="seconds"
            )
        )
        Activity(time=-3)
        Activity(time="Pippo")
        Activity(user_id=-1)
        Activity(user_id="1")
        Activity(activity_type="Login")
        Activity(activity_type="Pippo")
        Activity(activity_type="")
        Activity(activity_details=33)
