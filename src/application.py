from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import PositiveInt, EmailStr
from pydantic_extra_types.country import CountryAlpha2
from src.models import User, Activity, SuperUser, SuperUserRoles, ActivityTypes
from tools.db_operations import retrieve_items, insert_item
from tools.tools import short_uuid4_generator
import psycopg

env_values = dotenv_values("db/.env")

db_connection_config = {
    "host": "localhost",
    "dbname": env_values.get("POSTGRES_DB"),
    "user": env_values.get("POSTGRES_USER"),
    "password": env_values.get("POSTGRES_PASSWORD"),
}

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Hello, I'm good!"


@app.post("/users/")
def post_user(
    username: str,
    email: EmailStr,
    age: PositiveInt = None,
    country: CountryAlpha2 = None,
    connection_config=None,
) -> User:
    if connection_config is None:
        connection_config = db_connection_config
    user_id = short_uuid4_generator()

    user = User(
        user_id=user_id, username=username, email=email, age=age, country=country
    )
    with psycopg.connect(connection_config, autocommit=True) as conn:
        with conn.cursor() as cur:
            try:
                insert_item(user, "users", cur)
            except psycopg.errors.UniqueViolation:  # TODO: should I let SQL raise the error, since the email column is UNIQUE, or should
                # I let FastAPI handle it as a HTTPException? In this last case one obtains the 400
                # status code, which can be tested for. Test works now, otherwise.
                raise HTTPException(status_code=400, detail="Email already registered")

    return user


@app.post("/superusers/")
def post_superuser(
    username: str,
    email: EmailStr,
    role: SuperUserRoles,
    age: PositiveInt = None,
    country: CountryAlpha2 = None,
) -> SuperUser:
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
    connection_config=None,
) -> Activity:
    if connection_config is None:
        connection_config = db_connection_config
    activity_id = short_uuid4_generator()
    activity = Activity(
        activity_id=activity_id,
        time=time,
        user_id=user_id,
        activity_type=activity_type,
        activity_details=activity_details,
    )

    with psycopg.connect(connection_config, autocommit=True) as conn:
        with conn.cursor() as cur:
            user_ids = retrieve_items("user_id", "users", cur)
            if activity.user_id not in user_ids:
                raise HTTPException(status_code=404, detail="User ID not found")
            insert_item(activity, "activities", cur)
    return activity


@app.get("/activities/")
async def read_activities_by_userid(user_id: PositiveInt, connection_config) -> list:
    with psycopg.connect(connection_config, autocommit=True) as conn:
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
