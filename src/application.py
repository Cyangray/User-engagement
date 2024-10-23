from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, PositiveInt, EmailStr, StringConstraints

# from typing import Literal
from typing_extensions import Literal, Annotated, Optional
import datetime

app = FastAPI()


class User(BaseModel):
    user_id: PositiveInt
    username: Annotated[str, StringConstraints(min_length=2, pattern=r"^[a-zA-Z]*$")]
    email: EmailStr
    age: Optional[PositiveInt]
    country: Optional[Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]]


class SuperUser(User):
    superuser_id: PositiveInt
    role: Literal["admin", "moderator", "support"]


class Activity(BaseModel):
    activity_id: PositiveInt
    time: datetime.datetime
    user_id: PositiveInt
    activity_type: Literal["click", "login", "logout", "purchase"]
    activity_details: str


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Hello, I'm good!"
