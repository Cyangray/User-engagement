from freezegun import freeze_time

from src.models import (
    User,
    SuperUser,
    Activity,
    ActivityTypes,
    SuperUserRoles,
    create_user,
    create_superuser,
    create_activity,
)
import pytest
from datetime import datetime
from pydantic import ValidationError

mock_incomplete_data_user = {
    "user_id": 1,
    "username": "Pippo",
    "email": "aaa@bbb.cc",
}

mock_data_user = {
    "username": "Pippo",
    "email": "aaa@bbb.cc",
    "age": 23,
    "country": "GB",
}

mock_data_superuser = {
    "username": "Pippo",
    "email": "aaa@bbb.cc",
    "age": 23,
    "country": "GB",
    "role": SuperUserRoles.admin,
}

mock_data_activity = {
    "time": datetime(2024, 10, 23, 9, 41, 3),
    "activity_type": ActivityTypes.login,
    "activity_details": "First login of the day",
}


@freeze_time("2020-10-23 12:00:01")
def test_validity_models():
    user = create_user(
        username=mock_data_user["username"],
        email=mock_data_user["email"],
        age=mock_data_user["age"],
        country=mock_data_user["country"],
    )
    superuser = create_superuser(user, mock_data_superuser["role"])
    activity = create_activity(
        user=superuser,
        activity_type=mock_data_activity["activity_type"],
        activity_details=mock_data_activity["activity_details"],
    )

    mock_data_user["user_id"] = user.user_id
    mock_data_superuser["user_id"] = superuser.user_id
    mock_data_superuser["superuser_id"] = superuser.superuser_id
    mock_data_activity["user_id"] = activity.user_id
    mock_data_activity["activity_id"] = activity.activity_id
    mock_data_activity["time"] = datetime.strptime(
        "2020-10-23 12:00:01", "%Y-%m-%d %H:%M:%S"
    )

    assert user.model_dump() == mock_data_user
    assert superuser.model_dump() == mock_data_superuser
    assert activity.model_dump() == mock_data_activity


def test_invalid_user_data():
    user = User(**mock_data_user)
    with pytest.raises(ValueError):
        User(**mock_incomplete_data_user)
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


def test_invalid_activity():
    activity = Activity(**mock_data_activity)
    with pytest.raises(ValidationError):
        activity.activity_id = -1
    with pytest.raises(ValidationError):
        activity.time = datetime.now().isoformat(timespec="microseconds", sep="T")
    with pytest.raises(ValidationError):
        activity.time = datetime.now().isoformat(sep="T")
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
