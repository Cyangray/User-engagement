from devtools.generate_dataset_tools import (
    generate_fake_user,
    post_fake_user_to_DB,
    generate_dates,
    generate_session,
    post_session,
)
import pandas as pd
import matplotlib.pyplot as plt

N_USERS = 2
CLICKS_PER_MINUTE = 5
SESSION_LENGTH_HOURS = 3
SESSIONS_PER_YEAR = 10


# generate users
users = []
for n in range(N_USERS):
    fake_user = generate_fake_user()
    user = post_fake_user_to_DB(fake_user)
    users.append(user)
    # post_fake_user_to_DB(fake_user) #this probably doesn't work. Connect to database in this script

activities = []
for user in users:
    dates = generate_dates(sessions_per_year=SESSIONS_PER_YEAR)
    list_of_complete_activities_per_user = []
    for date in dates:
        list_of_fake_activities_in_session = generate_session(
            date, user.user_id, CLICKS_PER_MINUTE, SESSION_LENGTH_HOURS
        )
        list_of_complete_activities_per_user = [
            *list_of_complete_activities_per_user,
            *post_session(list_of_fake_activities_in_session),
        ]
    activities = activities + list_of_complete_activities_per_user


### collect data
df = pd.DataFrame([activity.__dict__ for activity in activities])

# plot e.g. activities grouped by hour
subset = df[df["activity_type"].isin(["click"])]
subset.groupby([subset["time"].dt.hour, "activity_type"]).size().unstack(
    fill_value=0
).plot(kind="bar")
plt.show()

# plot something for just one user (work in progress, but it shows that the code works)
subset = df[df["user_id"] == users[0].user_id]
subset = subset[["time", "activity_type"]]
subset.set_index("time", inplace=True)
subset = (
    subset.groupby("activity_type")
    .resample("W")
    .size()
    .unstack(fill_value=0)
    .transpose()
)
subset.plot(kind="bar", stacked=True)
plt.show()
