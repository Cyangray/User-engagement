from datetime import datetime
from enum import Enum
from pydantic import (
    BaseModel,
    PositiveInt,
    EmailStr,
    field_validator,
    model_validator,
    Field,
)
from typing import Self
from pydantic_extra_types.country import CountryAlpha2


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
    username: str = Field(min_length=2, pattern=r"^[a-zA-Z]*$")
    email: EmailStr
    age: PositiveInt | None
    country: CountryAlpha2 | None

    @model_validator(mode="after")
    def check_if_both_age_and_country(self) -> Self:
        age = self.age
        country = self.country
        if age is None and country is None:
            raise ValueError("Enter at least age or country")
        return self


class SuperUser(User, validate_assignment=True):
    superuser_id: PositiveInt
    role: SuperUserRoles


class Activity(BaseModel, validate_assignment=True):
    activity_id: PositiveInt
    time: datetime
    user_id: PositiveInt
    activity_type: ActivityTypes
    activity_details: str

    @field_validator("time", mode="before")
    def prevalidate_datetime(cls, entry):
        if isinstance(entry, str):
            try:
                return datetime.strptime(entry, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(
                    'Incorrect date string format, should be "YYYY-MM-DD HH:MM:SS" (UTC time)'
                )
        else:
            raise ValueError("Input format for time attribute should be a str.")
