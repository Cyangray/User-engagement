from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import PositiveInt, EmailStr
from pydantic_extra_types.country import CountryAlpha2

from src.models import User, Activity, SuperUser, SuperUserRoles, ActivityTypes
from tools.tools import short_uuid4_generator

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


@app.post("/users/", response_model=User)
def post_user(
    username: str,
    email: EmailStr,
    age: PositiveInt = None,
    country: CountryAlpha2 = None,
) -> User:
    user_id = short_uuid4_generator()
    user = User(
        user_id=user_id, username=username, email=email, age=age, country=country
    )
    if user.email in emails_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    users_id_db.append(user.user_id)
    users_db.append(user)
    emails_db.append(user.email)
    return user


@app.post("/superusers/", response_model=SuperUser)
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
    if superuser.email in emails_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    users_id_db.append(superuser.user_id)
    users_db.append(superuser)
    emails_db.append(superuser.email)
    superusers_id_db.append(superuser.user_id)
    superusers_db.append(superuser)
    return superuser


@app.post("/activities/", response_model=Activity)
async def post_activity(
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
    if activity.user_id not in users_id_db:
        raise HTTPException(status_code=404, detail="User ID not found")
    activities_id_db.append(activity.activity_id)
    activities_db.append(activity)
    return activity


@app.get("/activities/", response_model=list[Activity])
async def read_activities_by_userid(user_id: PositiveInt) -> list[Activity]:
    if user_id not in users_id_db:
        raise HTTPException(status_code=404, detail="User ID not found.")
    if user_id not in [item.user_id for item in activities_db]:
        raise HTTPException(
            status_code=404, detail=f"No activities by {user_id=} found."
        )
    return [item for item in activities_db if item.user_id == user_id]
