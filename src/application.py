from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import PositiveInt, EmailStr

from src.models import User, Activity, ActivityTypes, create_activity, create_user

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Hello, I'm good!"


superusers_id_db = [
    i for i in range(1, 100)
]  # TODO: placeholder. This should be created automatically when instantiating objects

users_db = []
emails_db = []
users_id_db = []
activities_db = []
activities_id_db = []


@app.post("/users/")
async def post_user(username, email: EmailStr, age=None, country=None) -> User:
    if email in emails_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    item = create_user(username, email, age, country)
    users_id_db.append(item.user_id)
    users_db.append(item)
    emails_db.append(email)
    return item


@app.post("/activities/")
async def post_activity(
    user_id: PositiveInt, activity_type: ActivityTypes, activity_details: str
) -> Activity:
    if user_id not in users_id_db:
        raise HTTPException(status_code=404, detail="User ID not found")
    item = create_activity(user_id, activity_type, activity_details)
    activities_id_db.append(item.activity_id)
    activities_db.append(item)
    return item


@app.get("/activities/")
async def read_activities_by_userid(user_id: PositiveInt):
    if user_id not in users_id_db:
        raise HTTPException(status_code=404, detail="User ID not found.")
    filtered_activities: list[Activity] = [
        activity for activity in activities_db if activity.user_id == user_id
    ]
    if len(filtered_activities) == 0:
        raise HTTPException(
            status_code=404, detail=f"No activities by {user_id=} found."
        )
    return filtered_activities
