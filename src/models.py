from datetime import datetime
from enum import Enum
from pydantic import PositiveInt, EmailStr, field_validator, model_validator, BaseModel
from typing import Self
from pydantic_extra_types.country import CountryAlpha2

import re


class ActivityTypes(str, Enum):
    click = "click"
    login = "login"
    logout = "logout"
    purchase = "purchase"


class SuperUserRoles(str, Enum):
    admin = "admin"
    moderator = "moderator"
    support = "support"


class User(BaseModel, validate_assignment=True):
    user_id: PositiveInt
    username: str
    email: EmailStr
    age: PositiveInt | None = None
    country: CountryAlpha2 | None = None

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
    role: SuperUserRoles


class Activity(BaseModel, validate_assignment=True):
    activity_id: PositiveInt
    time: datetime
    user_id: PositiveInt
    activity_type: ActivityTypes
    activity_details: str | None = None

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
