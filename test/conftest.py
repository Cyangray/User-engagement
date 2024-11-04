import pytest

from tools.tools import short_uuid4_generator


@pytest.fixture(scope="session")
def user_id():
    return short_uuid4_generator()


@pytest.fixture(scope="session")
def superuser_id():
    return short_uuid4_generator()


@pytest.fixture(scope="session")
def activity_id():
    return short_uuid4_generator()


# user_id = short_uuid4_generator()
# superuser_id = short_uuid4_generator()
# activity_id = short_uuid4_generator()


@pytest.fixture(scope="session")
def mock_incomplete_data_user(user_id):
    mock_incomplete_data_user = {
        "user_id": user_id,
        "username": "Pippo",
        "email": "aaa@bbb.cc",
    }
    return mock_incomplete_data_user


@pytest.fixture(scope="session")
def mock_data_user(user_id):
    mock_data_user = {
        "user_id": user_id,
        "username": "Pippo",
        "email": "aaa@bbb.cc",
        "age": 23,
        "country": "GB",
    }
    return mock_data_user


@pytest.fixture(scope="session")
def mock_data_user2(user_id):
    mock_data_user2 = {
        "user_id": user_id + 1,
        "username": "Pippo2",
        "email": "aaa2@bbb.cc",
        "age": 24,
        "country": "FR",
    }
    return mock_data_user2


@pytest.fixture(scope="session")
def mock_data_superuser(superuser_id):
    mock_data_superuser = {"superuser_id": superuser_id, "role": "admin"}
    return mock_data_superuser


@pytest.fixture(scope="session")
def mock_data_activity(user_id, activity_id):
    mock_data_activity = {
        "user_id": user_id,
        "activity_id": activity_id,
        "time": "2020-04-23T12:00:01Z",
        "activity_type": "login",
        "activity_details": "First login of the day",
    }
    return mock_data_activity


@pytest.fixture(scope="session")
def mock_data_superuser_complete(user_id, superuser_id):
    mock_data_superuser_complete = {
        "superuser_id": superuser_id,
        "user_id": user_id,
        "username": "Pippo",
        "email": "eee@bbb.cc",
        "age": 23,
        "country": "GB",
        "role": "admin",
    }
    return mock_data_superuser_complete
