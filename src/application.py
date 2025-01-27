from contextlib import asynccontextmanager

import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import PositiveInt, EmailStr
from pydantic_extra_types.country import CountryAlpha2
from src.models import User, Activity, SuperUser, SuperUserRoles, ActivityTypes
from tools.db_operations import retrieve_items, insert_item, sql_to_dataframe
from tools.tools import (
    short_uuid4_generator,
    long_uuid4_generator,
    filter_time,
    polish_activity_types_list,
    check_for_allowed_freq_string,
    validate_time_bin,
    validate_time_entries,
)
from tools.ConnectionManager import get_db
# import matplotlib.pyplot as plt #will be useful soon


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    lifespan function that yields a connection to the database that lasts until the code is shut down.
    :param application: FastAPI object, the app.
    """
    # At startup - start connection to the SQL server
    connection_manager = get_db()
    application.state.connection_manager = connection_manager
    yield
    # At shutdown - close the connection
    connection_manager.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get("/", response_class=PlainTextResponse)
async def root():
    """
    Main page text, that shows that the client is connected to the API.

    ## returns
    hello world string
    """
    return "Hello, I'm good!"


@app.post("/users/")
def post_user(
    username: str,
    email: EmailStr,
    age: PositiveInt = None,
    country: CountryAlpha2 = None,
) -> User:
    """
    Function that posts a user to the API, and adds it to the database. A check is done on whether a user with the same mail is present in the database. Although both age and country are optional, at least one of those must be provided, otherwise a ValidationError is thrown. It returns the user object.

    ## parameters
    **username** *string*: Username. Only letters, more than two.

    **email** *string*: Email. Must be in the form aaa@bbb.ccc.

    **age** *integer (optional)*: age in years.

    **country** *string (optional)*: Country alpha-2 code. Two capitalized letters. check https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements if in doubt.

    ## returns
    User object.
    """

    user_id = short_uuid4_generator()
    user = User(
        user_id=user_id, username=username, email=email, age=age, country=country
    )
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        emails = retrieve_items("email", "users", cur)
        if email in emails:
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            insert_item(user, "users", cur)

    return user


@app.post("/superusers/")
def post_superuser(
    username: str,
    email: EmailStr,
    role: SuperUserRoles,
    age: PositiveInt = None,
    country: CountryAlpha2 = None,
) -> SuperUser:
    """
    Function that posts a superuser to the API. A check is done on whether a user with the same mail is present in the database. It returns the superuser object.

    ## parameters
    **username** *string*: Username. Only letters, more than two.

    **email** *string*: Email. Must be in the form aaa@bbb.ccc.

    **age** *integer*: age in years.

    **country** *string*: Country alpha-2 code. Two capitalized letters. check https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements if in doubt.

    **role** *string*: Can only be "admin", "moderator" or "support".

    ## returns
    SuperUser object.
    """
    user_id = short_uuid4_generator()
    superuser = SuperUser(
        user_id=user_id,
        username=username,
        email=email,
        role=role,
        age=age,
        country=country,
    )
    return superuser


@app.post("/activities/")
async def post_activity(
    time: str,
    user_id: PositiveInt,
    activity_type: ActivityTypes,
    activity_details: str = None,
) -> Activity:
    """
    Posts an activity to the API, and adds it to the database. first, it checks if the provided userID exists. It returns an Activity object.

    ## parameters
    **time** *datetime object, or string*: The time the activity took place. If string, it must be in the form YYYY-MM-DDTHH:MM:SSZ.

    **user_id** *integer*: The user_id of the user doing the action.

    **activity_type** *string*: Can only be "click", "login", "logout" and "purchase".

    **activity_details** *string*: Details on the activity.

    ## returns
    Activity object.
    """
    activity_id = long_uuid4_generator()
    activity = Activity(
        activity_id=activity_id,
        time=time,
        user_id=user_id,
        activity_type=activity_type,
        activity_details=activity_details,
    )
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        user_ids = retrieve_items("user_id", "users", cur)
        if activity.user_id not in user_ids:
            raise HTTPException(status_code=404, detail="User ID not found")
        insert_item(activity, "activities", cur)
    return activity


@app.get("/activity_types_grouped/")
async def histogram_activity_types_grouped(
    time_bin: str = "hour",
    activity1: str = None,
    activity2: str = None,
    activity3: str = None,
    activity4: str = None,
    start_time: str = None,
    end_time: str = None,
    period_days: int = 30,
    period_hours: int = 0,
):
    """
    Function giving information about activities per time bin, given a time period. The user provides a time bin (hours, days, months...) and the function returns the amount of the given activity types per time bin.
    For the time period, either provide start and end times, or end time and period (in days and hours).

    ## Parameters

    **time_bin** *string*: time bin to use when grouping activity types. It may take the values "hour", "day", "month", "year".


    **activity1** to **activity4** *string*: The activity types to count. Each parameter may take the values "login", "logout", "purchase" and "click". If nothing is chosen, the default "login", "logout" and "purchase" are chosen.

    **start_time** and **end_time** *string in the YYYY-MM-DDTHH:MM:SSZ format*: Start and end times for the time period under consideration.

    **period_days** and **period_hours** *int*: If only end_time is provided, the start time is calculated from this time difference.
    """

    # validate input
    validate_time_entries(period_days, period_hours, start_time, end_time)
    validate_time_bin(time_bin)

    # Connect to database and extract dataframe
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        df = sql_to_dataframe("activities", cur)

    # filter for time period and activity type
    activity_types = polish_activity_types_list(
        [activity1, activity2, activity3, activity4],
        default=["login", "purchase", "logout"],
    )
    df = filter_time(df, start_time, end_time, period_days, period_hours)
    subset = df[df["activity_type"].isin(activity_types)]
    subset[time_bin] = getattr(df["time"].dt, time_bin)

    # group according to time bin
    subset.groupby([subset[time_bin], "activity_type"]).size().unstack(fill_value=0)
    return subset.to_html()  # TODO: fix output format later, and fix tests


@app.get("/total_activity_over_time/")
async def total_activity_over_time(
    activity1: str = None,
    activity2: str = None,
    activity3: str = None,
    activity4: str = None,
    start_time: str = None,
    end_time: str = None,
    period_days: int = 365,
    period_hours: int = 0,
    frequency: str = "MS",
):
    """
    Function giving information about activities over time, given a time period and frequency. The user provides a frequency (hours, days, months, quarter...) and the function returns the amount of the given activity types per time unit.
    For the time period, either provide start and end times, or end time and period (in days and hours).

    ## Parameters

    **activity1** to **activity4** *string*: The activity types to count. Each parameter may take the values "login", "logout", "purchase" and "click". If nothing is chosen, the default "login", "logout" and "purchase" are chosen.

    **start_time** and **end_time** *string in the YYYY-MM-DDTHH:MM:SSZ format*: Start and end times for the time period under consideration.

    **period_days** and **period_hours** *int*: If only end_time is provided, the start time is calculated from this time difference.

    **frequency** *str*: the time unit to subdivide the period in. It follows Panda's offset aliases scheme (https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases). Some of the mostly used strings are "min" (minutes), "h" (hours), "D" (day), "W" (week), "MS" (month start), "QS" (quarter start) and "YS" (year start). Combinations are also possible (e.g. "2D12h30min").
    """

    # validate input
    check_for_allowed_freq_string(frequency)
    validate_time_entries(period_days, period_hours, start_time, end_time)

    # Connect to database and extract dataframe
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        df = sql_to_dataframe("activities", cur)

    # filter for time period and activity type
    activity_types = polish_activity_types_list(
        [activity1, activity2, activity3, activity4],
        default=["login", "purchase", "logout"],
    )
    subset = filter_time(df, start_time, end_time, period_days, period_hours)
    subset = subset[subset["activity_type"].isin(activity_types)]

    # fill time bins
    subset = subset.groupby(["time", "activity_type"]).size().reset_index(name="count")
    subset = subset.pivot(index="time", columns="activity_type", values="count").fillna(
        0
    )
    subset = subset.groupby(pd.Grouper(freq=frequency)).sum()
    # TODO: in plot: stacked bars
    return subset.to_html()


@app.get("/purchases/")
async def avg_purchases(
    start_time: str = None,
    end_time: str = None,
    period_days: int = 30,
    period_hours: int = 0,
    frequency: str = "MS",
):
    """
    Function giving information about the average number of purchases per login, given a time period and frequency. The user provides a frequency (hours, days, months, quarter...) and the function returns the average number of purchases per login per chosen time unit.
    For the time period, either provide start and end times, or end time and period (in days and hours).

    ## Parameters

    **start_time** and **end_time** *string in the YYYY-MM-DDTHH:MM:SSZ format*: Start and end times for the time period under consideration.

    **period_days** and **period_hours** *int*: If only end_time is provided, the start time is calculated from this time difference.

    **frequency** *str*: the time unit to subdivide the period in. It follows Panda's offset aliases scheme (https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases). Some of the mostly used strings are "min" (minutes), "h" (hours), "D" (day), "W" (week), "MS" (month start), "QS" (quarter start) and "YS" (year start). Combinations are also possible (e.g. "2D12h30min").
    """

    # validate input
    check_for_allowed_freq_string(frequency)
    validate_time_entries(period_days, period_hours, start_time, end_time)

    # Connect to database and extract dataframe
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        df = sql_to_dataframe("activities", cur)

    # filter for time period and activity type
    activity_types = ["login", "purchase"]
    subset = filter_time(df, start_time, end_time, period_days, period_hours)
    subset = subset[subset["activity_type"].isin(activity_types)]

    # fill time bins
    subset = subset.groupby(["time", "activity_type"]).size().reset_index(name="count")
    subset = subset.pivot(index="time", columns="activity_type", values="count").fillna(
        0
    )
    subset = subset.groupby(pd.Grouper(freq=frequency)).sum()

    # calculate purchases per login per time bin
    subset["avg_purchases_per_login"] = subset["purchase"] / subset["login"]

    return subset.to_html()


@app.get("/avg_time/")
async def avg_time_spent(
    start_time: str = None,
    end_time: str = None,
    period_days: int = 30,
    period_hours: int = 0,
    frequency: str = "MS",
):
    """
    Function giving information about the average time spent per user session (calculated as time between logout and login). The user provides a frequency (hours, days, months, quarter...) and the function returns the average number of purchases per login per chosen time unit.
    For the time period, either provide start and end times, or end time and period (in days and hours).

    ## Parameters

    **start_time** and **end_time** *string in the YYYY-MM-DDTHH:MM:SSZ format*: Start and end times for the time period under consideration.

    **period_days** and **period_hours** *int*: If only end_time is provided, the start time is calculated from this time difference.

    **frequency** *str*: the time unit to subdivide the period in. It follows Panda's offset aliases scheme (https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases). Some of the mostly used strings are "min" (minutes), "h" (hours), "D" (day), "W" (week), "MS" (month start), "QS" (quarter start) and "YS" (year start). Combinations are also possible (e.g. "2D12h30min").
    """

    # validate input
    check_for_allowed_freq_string(frequency)
    validate_time_entries(period_days, period_hours, start_time, end_time)

    # Connect to database and extract dataframe
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        df = sql_to_dataframe("activities", cur)

    # filter for time period
    subset = filter_time(df, start_time, end_time, period_days, period_hours)

    # create new dataframe with session information (user_id, login_time, logout_time, duration)
    subset = subset[["time", "user_id", "activity_type"]]
    logins = subset[subset["activity_type"] == "login"].reset_index(drop=True)
    logouts = subset[subset["activity_type"] == "logout"].reset_index(drop=True)
    sessions = pd.DataFrame(
        {
            "user_id": logins["user_id"],
            "login_time": logins["time"],
            "logout_time": logouts["time"],
        }
    )
    sessions["duration"] = sessions["logout_time"] - sessions["login_time"]
    sessions = sessions.set_index("login_time")
    sessions = sessions.groupby(pd.Grouper(freq=frequency)).mean()

    return sessions.to_html()


@app.get("/activities/")
async def read_activities_by_userid(
    user_id: PositiveInt,
) -> list[dict]:
    """
    Function returning a list of activities filtered by user_id.

    ## parameters
    **user_id** *integer*: user_id of the user we want to filter for activities.

    ## returns
    list of Activity objects.
    """
    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        user_ids = retrieve_items("user_id", "users", cur)
        if user_id not in user_ids:
            raise HTTPException(status_code=404, detail="User ID not found.")
        user_id_activities = retrieve_items("user_id", "activities", cur)
        if user_id not in user_id_activities:
            raise HTTPException(
                status_code=404, detail=f"No activities by {user_id=} found."
            )

        query = f"""SELECT * FROM activities WHERE user_id = {user_id}"""
        act_list = cur.execute(query, {"user_id": user_id}).fetchall()
        act_list = [
            dict((cur.description[i][0], value) for i, value in enumerate(row))
            for row in act_list
        ]
    return act_list


# # plot something for just one user (work in progress, but it shows that the code works)
# subset = df[df["user_id"] == users[0].user_id]
# subset = subset[["time", "activity_type"]]
# subset.set_index("time", inplace=True)
# subset = (
#     subset.groupby("activity_type")
#     .resample("W")
#     .size()
#     .unstack(fill_value=0)
#     .transpose()
# )
# subset.plot(kind="bar", stacked=True)
# plt.show()
