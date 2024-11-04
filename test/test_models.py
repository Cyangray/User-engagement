from freezegun import freeze_time

from src.models import (
    ActivityTypes,
    SuperUserRoles,
    create_user,
    create_superuser,
    create_activity,
)
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError


@pytest.fixture(scope="session")
def mock_incomplete_user():
    mock_incomplete_data_user = {
        "username": "Pippo",
        "email": "aaa@bbb.cc",
    }
    return mock_incomplete_data_user


@pytest.fixture(scope="session")
def mock_user():
    mock_data_user = {
        "username": "Pippo",
        "email": "aaa@bbb.cc",
        "age": 23,
        "country": "GB",
    }
    return mock_data_user


@pytest.fixture(scope="session")
def mock_superuser():
    mock_data_superuser = {
        "user_id": 1,
        "username": "Pippo",
        "email": "aaa@bbb.cc",
        "age": 23,
        "country": "GB",
        "role": SuperUserRoles.admin,
    }
    return mock_data_superuser


@pytest.fixture(scope="session")
def mock_activity():
    mock_data_activity = {
        "user_id": 1,
        # "time": datetime(2024, 10, 23, 9, 41, 3),
        "activity_type": ActivityTypes.login,
        "activity_details": "First login of the day",
    }
    return mock_data_activity


@pytest.fixture(scope="session")
def frozen_time():
    return datetime(2020, 10, 23, 12, 00, 1, tzinfo=timezone.utc)


@freeze_time("2020-10-23T12:00:01+00:00")
def test_validity_models(mock_user, mock_superuser, mock_activity, frozen_time):
    mock_data_user = mock_user
    mock_data_superuser = mock_superuser
    mock_data_activity = mock_activity

    user = create_user(**mock_data_user)
    superuser = create_superuser(**mock_data_superuser)
    activity = create_activity(**mock_data_activity)

    assert "user_id" in user.__dict__
    assert user.username == mock_data_user["username"]
    assert user.email == mock_data_user["email"]
    assert user.age == mock_data_user["age"]
    assert user.country == mock_data_user["country"]

    assert "superuser_id" in superuser.__dict__
    assert superuser.user_id == mock_data_superuser["user_id"]
    assert superuser.username == mock_data_superuser["username"]
    assert superuser.email == mock_data_superuser["email"]
    assert superuser.age == mock_data_superuser["age"]
    assert superuser.country == mock_data_superuser["country"]
    assert superuser.role == mock_data_superuser["role"]

    assert "activity_id" in activity.__dict__
    assert activity.user_id == mock_data_activity["user_id"]
    assert activity.activity_details == mock_data_activity["activity_details"]
    assert activity.activity_type == mock_data_activity["activity_type"]
    assert isinstance(activity.time, datetime)
    assert activity.time == datetime.now(timezone.utc)


def test_invalid_user_data(mock_user, mock_incomplete_user):
    mock_data_user = mock_user
    mock_data_incomplete_user = mock_incomplete_user
    user = create_user(**mock_data_user)
    with pytest.raises(ValueError):
        create_user(**mock_data_incomplete_user)
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
    with pytest.raises(ValidationError):
        user.country = "QQ"


@freeze_time("2020-10-23T12:00:01Z")
def test_invalid_activity(mock_activity):
    mock_data_activity = mock_activity
    activity = create_activity(**mock_data_activity)
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


def test_invalid_superuser_data(mock_superuser):
    mock_data_superuser = mock_superuser
    superuser = create_superuser(**mock_data_superuser)
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
