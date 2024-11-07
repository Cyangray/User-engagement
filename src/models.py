from datetime import datetime
from enum import Enum
from pydantic import PositiveInt, EmailStr, field_validator, model_validator
from typing import Self
from pydantic_extra_types.country import CountryAlpha2

import re

from sqlmodel import SQLModel, Field


class ActivityTypes(str, Enum):
    click = "click"
    login = "login"
    logout = "logout"
    purchase = "purchase"


class SuperUserRoles(str, Enum):
    admin = "admin"
    moderator = "moderator"
    support = "support"


class User(SQLModel, validate_assignment=True, table=True):
    __tablename__ = "users"
    user_id: PositiveInt = Field(primary_key=True)
    username: str = Field(min_length=2, index=True)
    email: EmailStr = Field(index=True)
    age: PositiveInt | None = Field(default=None, index=True)
    country: CountryAlpha2 | None = Field(default=None, index=True)

    @field_validator("username", mode="before")
    def username_validator(cls, v):
        pattern = r"^[a-zA-Z]*$"
        if re.match(pattern, v) and len(v) >= 2:
            return v
        else:
            raise ValueError(
                "Username must contain only letters and be at least two characters long."
            )

    @model_validator(mode="after")
    def check_if_both_age_and_country(self) -> Self:
        age = self.age
        country = self.country
        if age is None and country is None:
            raise ValueError("Enter at least age or country")
        return self


class SuperUser(User, validate_assignment=True):
    role: SuperUserRoles = Field(index=True)


class Activity(SQLModel, validate_assignment=True, table=True):
    __tablename__ = "activities"
    activity_id: PositiveInt = Field(primary_key=True)
    time: datetime = Field(index=True)
    user_id: PositiveInt = Field(index=True)
    activity_type: ActivityTypes = Field(index=True)
    activity_details: str | None = Field(default=None, index=True)

    @field_validator("time", mode="before")
    def prevalidate_datetime(cls, entry):
        if isinstance(entry, str):
            if ("Z" in entry) or ("+00:00" in entry):
                return datetime.fromisoformat(entry)
            else:
                raise ValueError(
                    'Incorrect data format, should be "YYYY-MM-DDTHH:MM:SSZ" or "YYYY-MM-DDTHH:MM:SS+00:00" (UTC time)'
                )
        else:
            raise ValueError("Input format for time attribute should be a str.")
