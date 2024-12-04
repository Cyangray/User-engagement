from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import PositiveInt, EmailStr
from pydantic_extra_types.country import CountryAlpha2
from src.models import User, Activity, SuperUser, SuperUserRoles, ActivityTypes
from tools.db_operations import retrieve_items, insert_item, sql_to_dataframe
from tools.tools import short_uuid4_generator, long_uuid4_generator
from tools.ConnectionManager import get_db
# import pandas as pd
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


@app.get("/activity_data/")
async def histogram_activity_types(
    time_bin: str = "hour",
    activity1=None,
    activity2=None,
    activity3=None,
    activity4=None,
):
    # Only select the interesting activity types to plot
    activity_types_input = [activity1, activity2, activity3, activity4]
    activity_types = []
    if all(el is None for el in activity_types_input):
        activity_types = ["login", "purchase", "logout"]
    else:
        activity_types_input = list(
            filter(lambda x: x is not None, activity_types_input)
        )
        allowed_activities = [
            key for key, _ in ActivityTypes._value2member_map_.items()
        ]
        for activity_type in activity_types_input:
            if activity_type in allowed_activities:
                activity_types.append(activity_type)
            else:
                raise HTTPException(
                    status_code=404, detail=f"{activity_type}: No such activity type"
                )

    conn = app.state.connection_manager.connection
    with conn.cursor() as cur:
        df = sql_to_dataframe("activities", cur)

    subset = df[df["activity_type"].isin(activity_types)]
    if time_bin == "hour":
        subset.groupby([subset["time"].dt.hour, "activity_type"]).size().unstack(
            fill_value=0
        )  # .plot(kind="bar")
    elif time_bin == "day":
        subset.groupby([subset["time"].dt.day, "activity_type"]).size().unstack(
            fill_value=0
        )  # .plot(kind="bar")

    return subset.to_html()


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
