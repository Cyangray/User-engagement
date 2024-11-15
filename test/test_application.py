from dotenv import dotenv_values
import pytest
from src.application import app
import psycopg
from src.models import User, Activity
from tools.db_operations import insert_item
import os


def test_client_startup(client_test) -> None:
    response = client_test.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, I'm good!"


def test_db_connection():
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

    try:
        conn = psycopg.connect(**db_connection_config, autocommit=True)
    finally:
        conn.close()


def test_post_user(mock_data_user, create_test_tables, client_test) -> None:
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)

    response = client_test.post(
        "/users/",
        params={**mock_data_user},
    )
    data = response.json()
    assert "user_id" in data
    excluded_keys = ["user_id"]
    for key, value in mock_data_user.items():
        if key not in excluded_keys:
            assert data[key] == value
    assert response.status_code == 200


def test_duplicate_id(mock_data_user, create_test_tables) -> None:
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user1 = User(**mock_data_user)
        user2 = User(**mock_data_user)
        insert_item(user1, "users", cur)
        with pytest.raises(Exception):
            user2.email = "ddd@eee.ff"
            insert_item(user2, "users", cur)


def test_duplicate_email(mock_data_user, create_test_tables, client_test) -> None:
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user1 = User(**mock_data_user)
        user2 = User(**mock_data_user)
        insert_item(user1, "users", cur)
        user2.user_id = user1.user_id - 1
        response = client_test.post("/users/", params={**user2.__dict__})
        assert response.status_code == 400


def test_post_superuser(mock_data_superuser_complete, client_test) -> None:
    response = client_test.post("/superusers/", params=mock_data_superuser_complete)
    data = response.json()
    excluded_keys = ["user_id"]
    for key, value in mock_data_superuser_complete.items():
        if key not in excluded_keys:
            assert data[key] == value
    assert response.status_code == 200


def test_post_activity(
    mock_data_user, mock_data_activity, create_test_tables, client_test
) -> None:
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user = User(**mock_data_user)
        insert_item(user, "users", cur)

    response = client_test.post(
        "/activities/",
        params={**mock_data_activity},
    )
    data = response.json()
    assert "activity_id" in data
    excluded_keys = ["activity_id"]
    for key, value in mock_data_activity.items():
        if key not in excluded_keys:
            assert data[key] == value
    assert response.status_code == 200


def test_post_activity_no_userid(
    mock_data_user, mock_data_activity, create_test_tables, client_test
) -> None:
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user = User(**mock_data_user)
        insert_item(user, "users", cur)

    response = client_test.post(
        "/activities/",
        params={
            "user_id": mock_data_activity["user_id"] + 1,
            "activity_id": mock_data_activity["activity_id"],
            "time": mock_data_activity["time"],
            "activity_type": mock_data_activity["activity_type"],
            "activity_details": mock_data_activity["activity_details"],
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User ID not found"


def test_filter_activities_by_user_id(
    mock_data_user, mock_data_activity, create_test_tables, client_test, mock_data_user2
) -> None:
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user = User(**mock_data_user)
        insert_item(user, "users", cur)
        user2 = User(**mock_data_user2)
        insert_item(user2, "users", cur)
        activity = Activity(**mock_data_activity)
        insert_item(activity, "activities", cur)

    response = client_test.get(
        f"/activities/?user_id={mock_data_user["user_id"]}",
        params={"user_id": mock_data_user["user_id"]},
    )
    data = response.json()

    excluded_keys = ["activity_id"]
    for key, value in mock_data_activity.items():
        if key not in excluded_keys:
            assert data[0][key] == value
    assert response.status_code == 200


def test_fail_filter_activities_user_id_not_found(
    mock_data_user, mock_data_activity, create_test_tables, client_test
) -> None:
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user = User(**mock_data_user)
        insert_item(user, "users", cur)
        activity = Activity(**mock_data_activity)
        insert_item(activity, "activities", cur)

    wrong_id = mock_data_user["user_id"] + 1
    response = client_test.get(
        f"/activities/?user_id={wrong_id}",
        params={"user_id": wrong_id},
    )
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "User ID not found."
