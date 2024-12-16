from src.models import User, Activity, ActivityTypes
import datetime
from faker import Faker
import numpy as np
import math

from tools.db_operations import insert_item
from tools.tools import short_uuid4_generator, long_uuid4_generator

rng = np.random.default_rng()


def generate_fake_user(name=None, country=None, email=None, age=None):
    """
    function generating a dict to be passed for generation of a fake user. Same parameters as for User
    """
    fake = Faker()
    if name is None:
        name = fake.first_name()
    if country is None:
        country = fake.country_code()
    if email is None:
        email = fake.email()
    if age is None:
        age = fake.pyint(min_value=18, max_value=90)
    return {"username": name, "email": email, "country": country, "age": age}


def post_fake_user_to_DB(cursor, fake_user):
    """
    Function taking a dictionary as input, creating a User object, and posting it to database.
    """
    user = User(user_id=short_uuid4_generator(), **fake_user)
    insert_item(user, "users", cursor)
    return user


def generate_fake_activity(
    time=None, user_id=None, activity_type=None, activity_details=None
):
    """
    function generating a dict to be passed for generation of a fake activity. Same parameters as for Activity
    """
    fake = Faker()
    if time is None:
        time = fake.date_time_this_year(tzinfo=datetime.UTC)
    if user_id is None:
        user_id = short_uuid4_generator()
    if activity_type is None:
        activity_type = fake.enum(ActivityTypes)
    if activity_details is None:
        activity_details = fake.text(max_nb_chars=20)
    return {
        "time": time.isoformat(timespec="seconds"),
        "user_id": user_id,
        "activity_type": activity_type,
        "activity_details": activity_details,
    }


def post_fake_activity_to_DB(cursor, fake_activity):
    """
    Function taking a dictionary as input, creating an Activity object, and posting it to database.
    """
    activity = Activity(activity_id=long_uuid4_generator(), **fake_activity)
    insert_item(activity, "activities", cursor)


def generate_dates(sessions_per_year):
    """
    generate a list of variable length (averaging on 5) of dates within a year
    explanation: a fake user will have a session on the website for given hours, about 5 times a year, with 50% chance of buying something
    returns a list of datetime objects, with time set to midnight (00:00:00)
    """
    fake = Faker()
    n_sessions = math.ceil(rng.poisson(sessions_per_year))
    datetimes = [
        datetime.datetime.combine(
            fake.date_between(start_date="-1y"), datetime.time.min, tzinfo=datetime.UTC
        )
        for _ in range(n_sessions)
    ]
    return datetimes


def get_truncated_normal(rng, mean=0, sd=1, low=0, upp=10):
    """helper function generating a number from a normal distribution within a range"""
    number = rng.normal(mean, sd)
    while number < low or number > upp:
        number = rng.normal(mean, sd)
    return number


def generate_session(date, user_id, n_activities_per_minute, length_session):
    """
    Function generating a user session: one login, many clicks, maybe one purchase, and one logout
    :param date: one of the dates generated in "generate_dates". time set to midnight.
    :param user_id: The user_id of the user in the session
    :param n_activities_per_minute: parameter deciding the activity
    :param length_session: mean length of a session, in hours
    :return: list of Activity objects representing one user session
    """
    list_of_activities = []

    # login time: normally distributed between 6AM and 8PM
    login_time_seconds = get_truncated_normal(
        rng, mean=13 * 60 * 60, sd=2 * 60 * 60, low=6 * 60 * 60, upp=20 * 60 * 60
    )
    login_time = date + datetime.timedelta(seconds=login_time_seconds)

    list_of_activities.append(
        generate_fake_activity(time=login_time, user_id=user_id, activity_type="login")
    )
    session_duration = rng.poisson(length_session * 60 * 60)
    logout_time = login_time + datetime.timedelta(seconds=session_duration)

    # distribute click times
    click_time = login_time + datetime.timedelta(
        seconds=rng.poisson(60 / n_activities_per_minute)
    )
    while click_time < logout_time:
        list_of_activities.append(
            generate_fake_activity(
                time=click_time, user_id=user_id, activity_type="click"
            )
        )
        click_time = click_time + datetime.timedelta(
            seconds=rng.poisson(60 / n_activities_per_minute)
        )

    # purchase? time modelled as a gaussian around the logout time. if time < logout time, then purchase. 50% probability
    purchase_time_seconds_after_login = get_truncated_normal(
        rng,
        mean=session_duration,
        sd=10 * 60 * length_session,
        low=session_duration * 0.5,
        upp=20 * 60 * 60,
    )
    if purchase_time_seconds_after_login < session_duration:
        purchase_time = login_time + datetime.timedelta(
            seconds=purchase_time_seconds_after_login
        )
        list_of_activities.append(
            generate_fake_activity(
                time=purchase_time, user_id=user_id, activity_type="purchase"
            )
        )

    list_of_activities.append(
        generate_fake_activity(
            time=logout_time, user_id=user_id, activity_type="logout"
        )
    )

    return list_of_activities


def post_session(cursor, list_of_activities):
    """
    function posting a session to the database
    """
    for fake_activity in list_of_activities:
        post_fake_activity_to_DB(cursor, fake_activity)
