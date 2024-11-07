import pytest


@pytest.fixture(scope="session")
def user_id_test():
    return 164280569


@pytest.fixture(scope="session")
def activity_id_test():
    return 1157425173


@pytest.fixture(scope="session")
def mock_incomplete_data_user(user_id_test):
    mock_incomplete_data_user = {
        "user_id": user_id_test,
        "username": "Pippo",
        "email": "aaa@bbb.cc",
    }
    return mock_incomplete_data_user


@pytest.fixture(scope="session")
def mock_data_user(user_id_test):
    mock_data_user = {
        "user_id": user_id_test,
        "username": "Pippo",
        "email": "aaa@bbb.cc",
        "age": 23,
        "country": "GB",
    }
    return mock_data_user


@pytest.fixture(scope="session")
def mock_data_user2(user_id_test):
    mock_data_user2 = {
        "user_id": user_id_test + 1,
        "username": "Pippo2",
        "email": "aaa2@bbb.cc",
        "age": 24,
        "country": "FR",
    }
    return mock_data_user2


@pytest.fixture(scope="session")
def mock_data_superuser():
    mock_data_superuser = {"role": "admin"}
    return mock_data_superuser


@pytest.fixture(scope="session")
def mock_data_activity(user_id_test, activity_id_test):
    mock_data_activity = {
        "user_id": user_id_test,
        "activity_id": activity_id_test,
        "time": "2020-04-23T12:00:01Z",
        "activity_type": "login",
        "activity_details": "First login of the day",
    }
    return mock_data_activity


@pytest.fixture(scope="session")
def mock_data_superuser_complete(user_id_test):
    mock_data_superuser_complete = {
        "user_id": user_id_test,
        "username": "Pippo",
        "email": "eee@bbb.cc",
        "age": 23,
        "country": "GB",
        "role": "admin",
    }
    return mock_data_superuser_complete
