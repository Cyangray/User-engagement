from src.models import SuperUserRoles, ActivityTypes
from tools.tools import short_uuid4_generator

user_id = short_uuid4_generator()
superuser_id = short_uuid4_generator()
activity_id = short_uuid4_generator()

mock_incomplete_data_user = {
    "user_id": user_id,
    "username": "Pippo",
    "email": "aaa@bbb.cc",
}

mock_data_user = {
    "user_id": user_id,
    "username": "Pippo",
    "email": "aaa@bbb.cc",
    "age": 23,
    "country": "GB",
}

mock_data_user2 = {
    "user_id": user_id + 1,
    "username": "Pippo2",
    "email": "aaa2@bbb.cc",
    "age": 24,
    "country": "FR",
}

mock_data_superuser = {
    "superuser_id": superuser_id,
    "role": SuperUserRoles.admin,
}

mock_data_activity = {
    "user_id": user_id,
    "activity_id": activity_id,
    "time": "2020-04-23 12:00:01",
    "activity_type": ActivityTypes.login,
    "activity_details": "First login of the day",
}

mock_data_superuser_complete = {
    "superuser_id": superuser_id,
    "user_id": user_id,
    "username": "Pippo",
    "email": "eee@bbb.cc",
    "age": 23,
    "country": "GB",
    "role": SuperUserRoles.admin,
}
