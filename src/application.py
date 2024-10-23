from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI()


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
