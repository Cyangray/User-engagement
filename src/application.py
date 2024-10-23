from fastapi import FastAPI
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
