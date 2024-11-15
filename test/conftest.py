import pytest
import psycopg
from dotenv import dotenv_values
from src.application import app
from tools.ConnectionManager import ConnectionManager
from fastapi.testclient import TestClient
import os


@pytest.fixture(scope="session")
def db_connection():
    """
    Establishes odbc connection for the whole session
    :return: pyodbc connection class
    """
    env_path = ".env"
    if os.path.exists(env_path):
        env_values = dotenv_values(env_path)
        env_variables = ["POSTGRES_USER", "POSTGRES_DB", "POSTGRES_PASSWORD"]
        for env_variable in env_variables:
            os.environ[env_variable] = env_values.get(env_variable)

    db_connection_config = {
        "host": "localhost",
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }
    testdb_connection_config = {
        "host": "localhost",
        "dbname": "testdb",
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }

    with psycopg.connect(**db_connection_config, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP DATABASE IF EXISTS testdb")
            cur.execute("CREATE DATABASE testdb")

    connection_manager = ConnectionManager(testdb_connection_config)
    connection_manager.connect()
    connection_manager.connection.autocommit = True

    return connection_manager


@pytest.fixture(scope="session")
def client_test(db_connection):
    client_ = TestClient(app)
    app.state.connection_manager = db_connection
    return client_


@pytest.fixture(scope="session")
def create_test_tables():
    commands = """
                DROP TABLE IF EXISTS users;
                DROP TABLE IF EXISTS activities;
                CREATE TABLE users (
                user_id INT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                age SMALLINT,
                country VARCHAR(2)
                );
                CREATE TABLE activities (
                activity_id INT PRIMARY KEY,
                user_id INT,
                time TIMESTAMPTZ,
                activity_type TEXT,
                activity_details TEXT
                );
                """
    return commands


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
        "username": "Pippolino",
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
        "activity_details": "This is a test activity",
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
