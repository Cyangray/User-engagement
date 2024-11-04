from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import PositiveInt

from src.models import User, Activity, SuperUser

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
def post_user(user: User) -> User:
    if user.email in emails_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    users_id_db.append(user.user_id)
    users_db.append(user)
    emails_db.append(user.email)
    return user


@app.post("/superusers/", response_model=SuperUser)
def post_superuser(superuser: SuperUser) -> SuperUser:
    if superuser.email in emails_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    superusers_id_db.append(superuser.user_id)
    superusers_db.append(superuser)
    return superuser


@app.post("/activities/", response_model=Activity)
async def post_activity(activity: Activity) -> Activity:
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
