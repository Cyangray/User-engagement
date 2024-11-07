from src.models import (
    User,
    SuperUser,
    Activity,
)
import pytest


def test_validity_user(mock_data_user) -> None:
    user = User(**mock_data_user)
    excluded_keys = ["_sa_instance_state"]
    for key, value in mock_data_user.items():
        if key not in excluded_keys:
            assert user.__dict__[key] == value


def test_incomplete_user(mock_incomplete_data_user):
    with pytest.raises(ValueError):
        User(**mock_incomplete_data_user)


@pytest.mark.parametrize(
    "user_id",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [-1, "-1", "fffaf", 4.33, "4.33"]
    ],
)
def test_invalid_user_user_id(user_id, mock_data_user) -> None:
    user = User(**mock_data_user)
    user.user_id = user_id


@pytest.mark.parametrize(
    "username",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [12, "12", "Pippo222", 3.5, "3.5"]
    ],
)
def test_invalid_user_username(username, mock_data_user) -> None:
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
def test_invalid_user_email(email, mock_data_user) -> None:
    user = User(**mock_data_user)
    user.email = email


@pytest.mark.parametrize(
    "age", [pytest.param(item, marks=pytest.mark.xfail) for item in [-2, "-2"]]
)
def test_invalid_user_age(age, mock_data_user) -> None:
    user = User(**mock_data_user)
    user.age = age


@pytest.mark.parametrize(
    "country",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in ["XX", -2, "2", "Great Britain"]
    ],
)
def test_invalid_user_country(country, mock_data_user) -> None:
    user = User(**mock_data_user)
    user.country = country


def test_validity_superuser(mock_data_superuser_complete) -> None:
    superuser = SuperUser(**mock_data_superuser_complete)
    excluded_keys = ["_sa_instance_state"]
    for key, value in mock_data_superuser_complete.items():
        if key not in excluded_keys:
            assert superuser.__dict__[key] == value


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in ["Admin", "Pippo", "", 33]
    ],
)
def test_invalid_superuser_role(role, mock_data_superuser_complete) -> None:
    superuser = SuperUser(**mock_data_superuser_complete)
    superuser.role = role


def test_validity_activity(mock_data_activity) -> None:
    activity = Activity(**mock_data_activity)
    excluded_keys = ["_sa_instance_state"]
    for key, value in mock_data_activity.items():
        if key not in excluded_keys:
            assert activity.__dict__[key] == value


@pytest.mark.parametrize(
    "activity_id",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [-1, "-1", "fffaf", 4.33, "4.33"]
    ],
)
def test_invalid_activity_activity_id(activity_id, mock_data_activity) -> None:
    activity = Activity(**mock_data_activity)
    activity.activity_id = activity_id


@pytest.mark.parametrize(
    "time",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [
            -3,
            "Pippo",
        ]
    ],
)
def test_invalid_activity_time(time, mock_data_activity) -> None:
    activity = Activity(**mock_data_activity)
    activity.time = time


@pytest.mark.parametrize(
    "activity_type",
    [pytest.param(item, marks=pytest.mark.xfail) for item in ["Login", "Pippo", ""]],
)
def test_invalid_activity_activity_type(activity_type, mock_data_activity) -> None:
    activity = Activity(**mock_data_activity)
    activity.activity_type = activity_type


@pytest.mark.parametrize(
    "activity_details",
    [pytest.param(item, marks=pytest.mark.xfail) for item in [33, -1, 3.5]],
)
def test_invalid_activity_activity_detail(activity_details, mock_data_activity) -> None:
    activity = Activity(**mock_data_activity)
    activity.activity_details = activity_details
