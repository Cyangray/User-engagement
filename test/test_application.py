from dotenv import dotenv_values
from fastapi.testclient import TestClient
import pytest
from src.application import app
import psycopg
from src.models import User, Activity
from tools.db_operations import insert_item

client = TestClient(app)


def test_client_startup() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, I'm good!"


def test_db_connection():
    env_values = dotenv_values(".env")
    db_connection_config = {
        "host": "localhost",
        "dbname": env_values.get("POSTGRES_DB"),
        "user": env_values.get("POSTGRES_USER"),
        "password": env_values.get("POSTGRES_PASSWORD"),
    }
    try:
        conn = psycopg.connect(**db_connection_config, autocommit=True)
    finally:
        conn.close()


def test_post_user(
    mock_data_user, db_test_connection_config, create_test_tables
) -> None:
    with psycopg.connect(db_test_connection_config) as conn:
        with conn.cursor() as cur:
            cur.execute(create_test_tables)

    response = client.post(
        "/users/",
        params={**mock_data_user, "connection_config": db_test_connection_config},
    )
    data = response.json()
    assert "user_id" in data
    excluded_keys = ["user_id"]
    for key, value in mock_data_user.items():
        if key not in excluded_keys:
            assert data[key] == value
    assert response.status_code == 200


def test_duplicate_id_and_mail(
    mock_data_user, db_test_connection_config, create_test_tables
) -> None:
    with psycopg.connect(db_test_connection_config) as conn:
        with conn.cursor() as cur:
            cur.execute(create_test_tables)
            user1 = User(**mock_data_user)
            user2 = User(**mock_data_user)
            insert_item(user1, "users", cur)

            # test for duplicate ID
            with pytest.raises(Exception):
                user2.email = "ddd@eee.ff"
                insert_item(user2, "users", cur)

            # test for duplicate mail
            with pytest.raises(Exception):
                user2.user_id = user1.user_id - 1
                user2.email = user1.email
                insert_item(user2, "users", cur)


def test_post_superuser(mock_data_superuser_complete) -> None:
    response = client.post("/superusers/", params=mock_data_superuser_complete)
    data = response.json()
    excluded_keys = ["user_id"]
    for key, value in mock_data_superuser_complete.items():
        if key not in excluded_keys:
            assert data[key] == value
    assert response.status_code == 200


def test_post_activity(
    mock_data_user, mock_data_activity, db_test_connection_config, create_test_tables
) -> None:
    with psycopg.connect(db_test_connection_config) as conn:
        with conn.cursor() as cur:
            cur.execute(create_test_tables)
            user = User(**mock_data_user)
            insert_item(user, "users", cur)

    response = client.post(
        "/activities/",
        params={**mock_data_activity, "connection_config": db_test_connection_config},
    )
    data = response.json()
    assert "activity_id" in data
    excluded_keys = ["activity_id"]
    for key, value in mock_data_activity.items():
        if key not in excluded_keys:
            assert data[key] == value
    assert response.status_code == 200


def test_post_activity_no_userid(
    mock_data_user, mock_data_activity, db_test_connection_config, create_test_tables
) -> None:
    with psycopg.connect(db_test_connection_config) as conn:
        with conn.cursor() as cur:
            cur.execute(create_test_tables)

            user = User(**mock_data_user)
            insert_item(user, "users", cur)

    response = client.post(
        "/activities/",
        params={
            "user_id": mock_data_activity["user_id"] + 1,
            "activity_id": mock_data_activity["activity_id"],
            "time": mock_data_activity["time"],
            "activity_type": mock_data_activity["activity_type"],
            "activity_details": mock_data_activity["activity_details"],
            "connection_config": db_test_connection_config,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User ID not found"


def test_filter_activities_by_user_id(
    mock_data_user, mock_data_activity, db_test_connection_config, create_test_tables
) -> None:
    with psycopg.connect(db_test_connection_config) as conn:
        with conn.cursor() as cur:
            cur.execute(create_test_tables)
            user = User(**mock_data_user)
            insert_item(user, "users", cur)
            activity = Activity(**mock_data_activity)
            insert_item(activity, "activities", cur)

    response = client.get(
        f"/activities/?user_id={mock_data_user["user_id"]}",
        params={
            "user_id": mock_data_user["user_id"],
            "connection_config": db_test_connection_config,
        },
    )
    data = response.json()

    excluded_keys = ["activity_id"]
    for key, value in mock_data_activity.items():
        if key not in excluded_keys:
            assert data[0][key] == value
    assert response.status_code == 200


def test_fail_filter_activities_user_id_not_found(
    mock_data_user, mock_data_activity, db_test_connection_config, create_test_tables
) -> None:
    with psycopg.connect(db_test_connection_config) as conn:
        with conn.cursor() as cur:
            cur.execute(create_test_tables)
            user = User(**mock_data_user)
            insert_item(user, "users", cur)
            activity = Activity(**mock_data_activity)
            insert_item(activity, "activities", cur)

    wrong_id = mock_data_user["user_id"] + 1
    response = client.get(
        f"/activities/?user_id={wrong_id}",
        params={"user_id": wrong_id, "connection_config": db_test_connection_config},
    )
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "User ID not found."
