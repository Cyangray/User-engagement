import pytest
from src.application import app
from src.models import User, Activity
from tools.db_operations import insert_item


def test_client_startup(client_test) -> None:
    """
    Tests the startup of the client.
    :param client_test: The (test) client
    """
    response = client_test.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, I'm good!"


# def test_db_connection():
#     """
#     tests that connection to the database is established.
#     """
#     db_connection_config = {
#         "host": os.getenv("POSTGRES_HOST"),
#         "dbname": os.getenv("POSTGRES_DB"),
#         "user": os.getenv("POSTGRES_USER"),
#         "password": os.getenv("POSTGRES_PASSWORD"),
#         "port": os.getenv("POSTGRES_PORT")
#     }
#
#     try:
#         conn = psycopg.connect(**db_connection_config, autocommit=True)
#         assert conn is not None
#     finally:
#         conn.close()


def test_post_user(mock_data_user, create_test_tables, client_test) -> None:
    """
    tests that a valid user data is posted to the API, and returns status_code 200.
    """
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
    """
    Tests that a second user with the same user_id and different email as the first one, will not be passed to the database.
    """
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
    """
    Tests that a second user with the same email and different user_id as the first one, will not be passed to the API or the database.
    """
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
    """
    Tests that a valid superuser will be passed to the API.
    """
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
    """
    Tests that a valid activity will be passed to the API.
    """
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
    """
    Failtests that an error is raised if one tries to post an activity with a user_id not present in the database.
    """
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


def test_histogram_activity_types_grouped(
    create_test_tables,
    mock_data_activity,
    mock_data_activity2,
    mock_data_activity3,
    client_test,
    mock_data_user,
):
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user = User(**mock_data_user)
        insert_item(user, "users", cur)
        activity1 = Activity(**mock_data_activity)
        activity2 = Activity(**mock_data_activity2)
        activity3 = Activity(**mock_data_activity3)
        insert_item(activity1, "activities", cur)
        insert_item(activity2, "activities", cur)
        insert_item(activity3, "activities", cur)

    response = client_test.get(
        "/activity_types_grouped/",
        params={
            "time_bin": "hour",
            "activity1": "login",
            "activity2": "logout",
            "activity3": "purchase",
            "period_days": "30",
            "period_hours": "0",
        },
    )

    assert response.status_code == 200
    # TODO: expand test with expected result, when the main function's output is fixed


def test_total_activity_over_time(
    create_test_tables,
    mock_data_activity,
    mock_data_activity2,
    mock_data_activity3,
    client_test,
    mock_data_user,
):
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user = User(**mock_data_user)
        insert_item(user, "users", cur)
        activity1 = Activity(**mock_data_activity)
        activity2 = Activity(**mock_data_activity2)
        activity3 = Activity(**mock_data_activity3)
        insert_item(activity1, "activities", cur)
        insert_item(activity2, "activities", cur)
        insert_item(activity3, "activities", cur)

    response = client_test.get(
        "/total_activity_over_time/",
        params={
            "time_bin": "hour",
            "activity1": "login",
            "activity2": "logout",
            "activity3": "purchase",
        },
    )

    assert response.status_code == 200
    # TODO: expand test with expected result, when the main function's output is fixed


def test_avg_purchases(
    create_test_tables,
    mock_data_activity,
    mock_data_activity2,
    mock_data_activity3,
    client_test,
    mock_data_user,
):
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user = User(**mock_data_user)
        insert_item(user, "users", cur)
        activity1 = Activity(**mock_data_activity)
        activity2 = Activity(**mock_data_activity2)
        activity3 = Activity(**mock_data_activity3)
        insert_item(activity1, "activities", cur)
        insert_item(activity2, "activities", cur)
        insert_item(activity3, "activities", cur)

    response = client_test.get(
        "/purchases/",
        params={
            "end_time": "2020-04-23T16:00:01Z",
            "period_days": "1",
            "period_hours": "0",
            "frequency": "h",
        },
    )

    assert response.status_code == 200
    # TODO: expand test with expected result, when the main function's output is fixed


def test_avg_time_spent(
    create_test_tables,
    mock_data_activity,
    mock_data_activity2,
    mock_data_activity3,
    client_test,
    mock_data_user,
):
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        cur.execute(create_test_tables)
        user = User(**mock_data_user)
        insert_item(user, "users", cur)
        activity1 = Activity(**mock_data_activity)
        activity2 = Activity(**mock_data_activity2)
        activity3 = Activity(**mock_data_activity3)
        insert_item(activity1, "activities", cur)
        insert_item(activity2, "activities", cur)
        insert_item(activity3, "activities", cur)

    response = client_test.get(
        "/avg_time/",
        params={
            "frequency": "MS",
        },
    )

    assert response.status_code == 200
    # TODO: expand test with expected result, when the main function's output is fixed


def test_filter_activities_by_user_id(
    mock_data_user, mock_data_activity, create_test_tables, client_test, mock_data_user2
) -> None:
    """
    Tests that the read_activities_by_userid works given valid input.
    """
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
    """
    Failtests that the read_activities_by_userid function in application.py will throw an error if there is no userid matching the query.
    """
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
