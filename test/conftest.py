import pandas as pd
import pytest
from dotenv import dotenv_values
from src.application import app
from src.models import Activity
from tools.ConnectionManager import ConnectionManager
from fastapi.testclient import TestClient
import os


@pytest.fixture(scope="session")
def db_connection():
    """
    Establishes postgresql connection for the whole session
    :return: Connection_Manager object
    """
    env_path = ".env"
    if os.path.exists(env_path):
        env_values = dotenv_values(env_path)
        env_variables = [
            "TEST_POSTGRES_USER",
            "TEST_POSTGRES_DB",
            "TEST_POSTGRES_PASSWORD",
            "TEST_POSTGRES_PORT",
            "TEST_POSTGRES_HOST",
        ]
        for env_variable in env_variables:
            os.environ[env_variable] = env_values.get(env_variable)

    testdb_connection_config = {
        "host": os.getenv("TEST_POSTGRES_HOST"),
        "dbname": os.getenv("TEST_POSTGRES_DB"),
        "user": os.getenv("TEST_POSTGRES_USER"),
        "password": os.getenv("TEST_POSTGRES_PASSWORD"),
        "port": os.getenv("TEST_POSTGRES_PORT"),
    }

    connection_manager = ConnectionManager(testdb_connection_config)
    connection_manager.connect()
    connection_manager.connection.autocommit = True

    return connection_manager


@pytest.fixture(scope="session")
def client_test(db_connection):
    """
    Establishes a connection between the client and the API.
    :param db_connection: fixture
    :return: the client
    """
    client_ = TestClient(app)
    app.state.connection_manager = db_connection
    return client_


@pytest.fixture(scope="session")
def create_test_tables():
    """
    Helper fixture saving the command to erase and rebuild the SQL tables to be used in tests.
    :return: a list of SQL commands.
    """
    commands = """
                DROP TABLE IF EXISTS activities;
                DROP TABLE IF EXISTS users;
                CREATE TABLE users (
                user_id INT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                age SMALLINT,
                country VARCHAR(2)
                );
                CREATE TABLE activities (
                activity_id UUID PRIMARY KEY,
                user_id INT REFERENCES users (user_id),
                time TIMESTAMPTZ,
                activity_type TEXT,
                activity_details TEXT
                );
                """
    return commands


@pytest.fixture(scope="session")
def user_id_test():
    """
    Fixture always returning the same user_id for tests.
    """
    return 164280569


@pytest.fixture(scope="session")
def activity_id_test():
    """
    Fixture always returning the same activity_id for tests.
    """
    return "8e1ec19c-02e4-408b-93c1-9664e800e772"


@pytest.fixture(scope="session")
def mock_incomplete_data_user(user_id_test):
    """
    Fixture returning an incomplete test user to be used in failtests.
    """
    mock_incomplete_data_user = {
        "user_id": user_id_test,
        "username": "Pippo",
        "email": "aaa@bbb.cc",
    }
    return mock_incomplete_data_user


@pytest.fixture(scope="session")
def mock_data_user(user_id_test):
    """
    Fixture returning a test user to be used in tests.
    """
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
    """
    Fixture returning a second test user to be used in tests.
    """
    mock_data_user2 = {
        "user_id": user_id_test + 1,
        "username": "Pippolino",
        "email": "aaa2@bbb.cc",
        "age": 24,
        "country": "FR",
    }
    return mock_data_user2


@pytest.fixture(scope="session")
def mock_data_superuser():
    """
    Fixture returning a test superuser to be used in tests.
    """
    mock_data_superuser = {"role": "admin"}
    return mock_data_superuser


@pytest.fixture(scope="session")
def mock_data_activity(user_id_test, activity_id_test):
    """
    Fixture returning a test activity to be used in tests. The user_id is linked to the first test_user.
    """
    mock_data_activity = {
        "user_id": user_id_test,
        "activity_id": activity_id_test,
        "time": "2020-04-23T12:00:01Z",
        "activity_type": "login",
        "activity_details": "This is a test activity",
    }
    return mock_data_activity


@pytest.fixture(scope="session")
def mock_data_activity2(user_id_test, activity_id_test):
    """
    Fixture returning a test activity to be used in tests. The user_id is linked to the first test_user.
    """
    activity_id_test2 = activity_id_test[:-1] + "3"

    mock_data_activity = {
        "user_id": user_id_test,
        "activity_id": activity_id_test2,
        "time": "2020-04-23T14:00:01Z",
        "activity_type": "purchase",
        "activity_details": "This is a test activity",
    }
    return mock_data_activity


@pytest.fixture(scope="session")
def mock_data_activity3(user_id_test, activity_id_test):
    """
    Fixture returning a test activity to be used in tests. The user_id is linked to the first test_user.
    """
    activity_id_test3 = activity_id_test[:-1] + "4"
    mock_data_activity = {
        "user_id": user_id_test,
        "activity_id": activity_id_test3,
        "time": "2020-04-23T16:00:01Z",
        "activity_type": "logout",
        "activity_details": "This is a test activity",
    }
    return mock_data_activity


@pytest.fixture(scope="session")
def mock_data_superuser_complete(user_id_test):
    """
    Fixture returning a test superuser to be used in tests.
    """
    mock_data_superuser_complete = {
        "user_id": user_id_test,
        "username": "Pippo",
        "email": "eee@bbb.cc",
        "age": 23,
        "country": "GB",
        "role": "admin",
    }
    return mock_data_superuser_complete


@pytest.fixture(scope="session")
def mock_dataframe(
    activity_id_test, mock_data_activity, mock_data_activity2, mock_data_activity3
):
    activity1 = Activity(**mock_data_activity)
    activity2 = Activity(**mock_data_activity2)
    activity3 = Activity(**mock_data_activity3)

    df = pd.DataFrame([activity1.__dict__, activity2.__dict__, activity3.__dict__])
    return df
