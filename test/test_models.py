from src.models import (
    User,
    SuperUser,
    Activity,
)
import pytest
from datetime import datetime
from test.conftest import mock_data_user, mock_data_superuser, mock_data_activity


def test_validity_user():
    user = User(**mock_data_user)
    assert "user_id" in user.__dict__
    assert user.username == mock_data_user["username"]
    assert user.email == mock_data_user["email"]
    assert user.age == mock_data_user["age"]
    assert user.country == mock_data_user["country"]


@pytest.mark.parametrize(
    "user_id",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [-1, "-1", "fffaf", 4.33, "4.33"]
    ],
)
def test_invalid_user_user_id(user_id):
    user = User(**mock_data_user)
    user.user_id = user_id


@pytest.mark.parametrize(
    "username",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [12, "12", "Pippo222", 3.5, "3.5"]
    ],
)
def test_invalid_user_username(username):
    user = User(**mock_data_user)
    user.username = username


@pytest.mark.parametrize(
    "email",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [
            12,
            "12",
            "Pippo222",
            3.5,
            "3.5",
            "ff@ff",
            "ff.ff",
            "@f.no",
            "e@.no",
        ]
    ],
)
def test_invalid_user_email(email):
    user = User(**mock_data_user)
    user.email = email


@pytest.mark.parametrize(
    "age", [pytest.param(item, marks=pytest.mark.xfail) for item in [-2, "-2"]]
)
def test_invalid_user_age(age):
    user = User(**mock_data_user)
    user.age = age


@pytest.mark.parametrize(
    "country",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in ["XX", -2, "2", "Great Britain"]
    ],
)
def test_invalid_user_country(country):
    user = User(**mock_data_user)
    user.country = country


def test_validity_superuser():
    superuser = SuperUser(**mock_data_user, **mock_data_superuser)
    assert "user_id" in superuser.__dict__
    assert "superuser_id" in superuser.__dict__
    assert superuser.username == mock_data_user["username"]
    assert superuser.email == mock_data_user["email"]
    assert superuser.age == mock_data_user["age"]
    assert superuser.country == mock_data_user["country"]
    assert superuser.role == mock_data_superuser["role"]


@pytest.mark.parametrize(
    "superuser_id",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [-1, "-1", "fffaf", 4.33, "4.33"]
    ],
)
def test_invalid_superuser_superuser_id(superuser_id):
    superuser = SuperUser(**mock_data_user, **mock_data_superuser)
    superuser.superuser_id = superuser_id


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in ["Admin", "Pippo", "", 33]
    ],
)
def test_invalid_superuser_role(role):
    superuser = SuperUser(**mock_data_user, **mock_data_superuser)
    superuser.role = role


def test_validity_activity():
    activity = Activity(**mock_data_activity)
    assert "activity_id" in activity.__dict__
    assert activity.user_id == mock_data_activity["user_id"]
    assert activity.activity_details == mock_data_activity["activity_details"]
    assert activity.activity_type == mock_data_activity["activity_type"]
    assert isinstance(activity.time, datetime)
    assert activity.time == datetime.strptime(
        mock_data_activity["time"], "%Y-%m-%d %H:%M:%S"
    )


@pytest.mark.parametrize(
    "activity_id",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [-1, "-1", "fffaf", 4.33, "4.33"]
    ],
)
def test_invalid_activity_activity_id(activity_id):
    activity = Activity(**mock_data_activity)
    activity.activity_id = activity_id


@pytest.mark.parametrize(
    "time",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [
            datetime.now().isoformat(timespec="microseconds", sep="T"),
            -3,
            "Pippo",
            datetime.now().isoformat(sep="T"),
        ]
    ],
)
def test_invalid_activity_time(time):
    activity = Activity(**mock_data_activity)
    activity.time = time


@pytest.mark.parametrize(
    "activity_type",
    [pytest.param(item, marks=pytest.mark.xfail) for item in ["Login", "Pippo", ""]],
)
def test_invalid_activity_activity_type(activity_type):
    activity = Activity(**mock_data_activity)
    activity.activity_type = activity_type


@pytest.mark.parametrize(
    "activity_details",
    [pytest.param(item, marks=pytest.mark.xfail) for item in [33, -1, 3.5]],
)
def test_invalid_activity_activity_detail(activity_details):
    activity = Activity(**mock_data_activity)
    activity.activity_details = activity_details
