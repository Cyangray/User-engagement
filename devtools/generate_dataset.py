from devtools.generate_dataset_tools import (
    generate_fake_user,
    post_fake_user_to_DB,
    generate_dates,
    generate_session,
    post_session,
    create_test_tables,
)

from tools.ConnectionManager import get_db

N_USERS = 5
CLICKS_PER_MINUTE = 3
SESSION_LENGTH_HOURS = 2
SESSIONS_PER_YEAR = 5

if __name__ == "__main__":
    print("writing fake data to database...")
    connection_manager = get_db()
    cursor = connection_manager.connection.cursor()
    cursor.execute(create_test_tables())
    # generate users
    users = []
    for n in range(N_USERS):
        fake_user = generate_fake_user()
        user = post_fake_user_to_DB(cursor, fake_user)
        users.append(user)

    for user in users:
        dates = generate_dates(sessions_per_year=SESSIONS_PER_YEAR)
        for date in dates:
            list_of_fake_activities_in_session = generate_session(
                date, user.user_id, CLICKS_PER_MINUTE, SESSION_LENGTH_HOURS
            )
            post_session(cursor, list_of_fake_activities_in_session)
    connection_manager.disconnect()
    print("Fake data generated and posted to database.")
