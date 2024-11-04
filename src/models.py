from datetime import datetime, timezone
from enum import Enum
from pydantic import (
    BaseModel,
    PositiveInt,
    StringConstraints,
    EmailStr,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated, Optional, Self
from tools.tools import short_uuid4_generator
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
    username: Annotated[str, StringConstraints(min_length=2, pattern=r"^[a-zA-Z]*$")]
    email: EmailStr
    age: Optional[PositiveInt]
    country: Optional[CountryAlpha2]

    @model_validator(mode="after")
    def check_if_both_age_and_country(self) -> Self:
        age = self.age
        country = self.country
        if age is None and country is None:
            raise ValueError("Enter at least age or country")
        return self


class SuperUser(BaseModel, validate_assignment=True):
    user_id: PositiveInt
    username: Annotated[str, StringConstraints(min_length=2, pattern=r"^[a-zA-Z]*$")]
    email: EmailStr
    age: Optional[PositiveInt]
    country: Optional[CountryAlpha2]
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
        if isinstance(entry, int):
            raise ValueError("Integers are not valid datetime entries")
        if isinstance(entry, str):
            try:
                print(entry)
                return datetime.fromisoformat(entry)
            except ValueError:
                raise ValueError(
                    'Incorrect data format, should be "YYYY-MM-DDTHH:MM:SSZ" or "YYYY-MM-DDTHH:MM:SS+00:00" (UTC time)'
                )
        return entry


def create_user(username, email, age=None, country=None) -> User:
    user_id = short_uuid4_generator()
    return User(
        user_id=user_id, username=username, email=email, age=age, country=country
    )


def create_superuser(
    user_id, username, email, role: SuperUserRoles, age=None, country=None
) -> SuperUser:
    superuser_id = short_uuid4_generator()
    return SuperUser(
        superuser_id=superuser_id,
        role=role,
        user_id=user_id,
        username=username,
        email=email,
        age=age,
        country=country,
    )


def create_activity(
    user_id, activity_type: ActivityTypes, activity_details: str
) -> Activity:
    activity_id = short_uuid4_generator()
    time = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    return Activity(
        activity_id=activity_id,
        activity_type=activity_type,
        activity_details=activity_details,
        time=time,
        user_id=user_id,
    )
