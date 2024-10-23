from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import (
    BaseModel,
    PositiveInt,
    EmailStr,
    StringConstraints,
    field_validator,
)

# from typing import Literal
from typing_extensions import Literal, Annotated, Optional
from datetime import datetime

app = FastAPI()


class User(BaseModel, validate_assignment=True):
    user_id: PositiveInt
    username: Annotated[str, StringConstraints(min_length=2, pattern=r"^[a-zA-Z]*$")]
    email: EmailStr
    age: Optional[PositiveInt]
    country: Optional[Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]]


class SuperUser(User, validate_assignment=True):
    superuser_id: PositiveInt
    role: Literal["admin", "moderator", "support"]


class Activity(BaseModel, validate_assignment=True):
    activity_id: PositiveInt
    time: datetime
    user_id: PositiveInt
    activity_type: Literal["click", "login", "logout", "purchase"]
    activity_details: str

    @field_validator("time", mode="before")
    def no_int_to_datetime(cls, entry):
        if isinstance(entry, int):
            raise ValueError("Integers are not valid datetime entries")
        return entry


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Hello, I'm good!"


users_id_db = [
    i for i in range(1, 100)
]  # TODO: placeholder. This should be created automatically when instantiating objects
superusers_id_db = [
    i for i in range(1, 100)
]  # TODO: placeholder. This should be created automatically when instantiating objects
activities_id_db = [
    i for i in range(1, 100)
]  # TODO: placeholder. This should be created automatically when instantiating objects
activities_db = []


@app.post("/activities/")
async def create_activity(item: Activity):
    activities_db.append(item)
    return item


@app.get("/activities/")
async def read_activities_by_userid(user_id: PositiveInt):
    if user_id not in users_id_db:
        raise HTTPException(status_code=404, detail="User not found.")
    filtered_activities: list[Activity] = [
        activity for activity in activities_db if activity.user_id == user_id
    ]
    if len(filtered_activities) == 0:
        raise HTTPException(
            status_code=404, detail=f"No activities by {user_id=} found."
        )
    return filtered_activities
