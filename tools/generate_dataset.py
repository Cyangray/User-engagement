from tools.generate_dataset_tools import (
    generate_fake_user,
    post_fake_user_to_DB,
    generate_dates,
    generate_session,
    post_session,
    create_test_tables,
)

from tools.ConnectionManager import get_db

N_USERS = 20
CLICKS_PER_MINUTE = 1
SESSION_LENGTH_HOURS = 2
SESSIONS_PER_YEAR = 10


def generate_dataset(
    n_users,
    clicks_per_minute,
    session_length_hours,
    sessions_per_year,
    connection_manager=None,
):
    print("writing fake data to database...")
    close = False
    if not connection_manager:
        close = True
        connection_manager = get_db()
    cursor = connection_manager.connection.cursor()
    cursor.execute(create_test_tables())
    # generate users
    users = []
    for n in range(n_users):
        fake_user = generate_fake_user()
        user = post_fake_user_to_DB(cursor, fake_user)
        users.append(user)

    for user in users:
        dates = generate_dates(sessions_per_year=sessions_per_year)
        for date in dates:
            list_of_fake_activities_in_session = generate_session(
                date, user.user_id, clicks_per_minute, session_length_hours
            )
            post_session(cursor, list_of_fake_activities_in_session)
    if close:
        connection_manager.disconnect()
    print("Fake data generated and posted to database.")


if __name__ == "__main__":
    generate_dataset(
        N_USERS, CLICKS_PER_MINUTE, SESSION_LENGTH_HOURS, SESSIONS_PER_YEAR
    )
