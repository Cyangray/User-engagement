from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from pydantic import PositiveInt, EmailStr
from pydantic_extra_types.country import CountryAlpha2

from src.models import User, Activity, SuperUser, SuperUserRoles, ActivityTypes
from tools.tools import short_uuid4_generator

from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL, create_engine
from dotenv import dotenv_values

env_values = dotenv_values("db/.env")

url_obj = URL.create(
    "postgresql+psycopg2",
    username=env_values.get("POSTGRES_USER"),
    password=env_values.get("POSTGRES_PASSWORD"),
    host="localhost",
    database=env_values.get("POSTGRES_DB"),
)

engine = create_engine(url_obj)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    with Session() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Hello, I'm good!"


emails_db = []
users_db = []
superusers_db = []
activities_db = []
users_id_db = []
superusers_id_db = []
activities_id_db = []


@app.post("/users/")
def post_user(
    session: SessionDep,
    username: str,
    email: EmailStr,
    age: PositiveInt = None,
    country: CountryAlpha2 = None,
) -> User:
    user_id = short_uuid4_generator()
    user = User(
        user_id=user_id, username=username, email=email, age=age, country=country
    )
    if user.email in emails_db:  # TODO: Change when global db deleted?
        raise HTTPException(status_code=400, detail="Email already registered")

    session.add(user)
    session.commit()
    session.refresh(user)

    users_id_db.append(user.user_id)  # TODO: delete later?
    users_db.append(user)
    emails_db.append(user.email)
    return user


@app.post("/superusers/", response_model=SuperUser)
def post_superuser(
    user_id: PositiveInt,
    username: str,
    email: EmailStr,
    role: SuperUserRoles,
    age: PositiveInt = None,
    country: CountryAlpha2 = None,
) -> SuperUser:
    superuser = SuperUser(
        user_id=user_id,
        username=username,
        email=email,
        role=role,
        age=age,
        country=country,
    )
    if superuser.email in emails_db:  # TODO: Change when global db deleted?
        raise HTTPException(status_code=400, detail="Email already registered")
    superusers_id_db.append(superuser.user_id)  # TODO: delete later?
    superusers_db.append(superuser)
    return superuser


@app.post("/activities/", response_model=Activity)
async def post_activity(
    session: SessionDep,
    time: str,
    user_id: PositiveInt,
    activity_type: ActivityTypes,
    activity_details: str = None,
) -> Activity:
    activity_id = short_uuid4_generator()
    activity = Activity(
        activity_id=activity_id,
        time=time,
        user_id=user_id,
        activity_type=activity_type,
        activity_details=activity_details,
    )
    if activity.user_id not in users_id_db:  # TODO: Change when global db deleted?
        raise HTTPException(status_code=404, detail="User ID not found")
    session.add(activity)
    session.commit()
    session.refresh(activity)
    activities_id_db.append(activity.activity_id)  # TODO: delete later?
    activities_db.append(activity)
    return activity


@app.get("/activities/", response_model=list[Activity])
async def read_activities_by_userid(user_id: PositiveInt) -> list[Activity]:
    if user_id not in users_id_db:  # TODO: Change when global db deleted?
        raise HTTPException(status_code=404, detail="User ID not found.")
    if user_id not in [
        item.user_id for item in activities_db
    ]:  # TODO: Change when global db deleted?
        raise HTTPException(
            status_code=404, detail=f"No activities by {user_id=} found."
        )
    return [
        item for item in activities_db if item.user_id == user_id
    ]  # TODO: Change when global db deleted?
