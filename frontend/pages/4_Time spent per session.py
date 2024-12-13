import os

import streamlit as st
import pandas as pd
import datetime
import requests
from io import StringIO
import altair as alt

st.title("Time spent per session")
st.markdown("## Input values")
st.write(
    "Provide either start date and time, or days/hours back. If end date is not provided, today is chosen by default."
)
col1, col2, col3 = st.columns(3)

days_back = col1.number_input("days back", value=365)
hours_back = col1.number_input("hours back", value=0)
frequency = col1.text_input("frequency", "MS")
start_date = col2.date_input("start date", None)
start_time = col2.time_input("start time", datetime.time.min)
end_date = col3.date_input("end date", None)
end_time = col3.time_input("end time", datetime.time.max)

start_datetime = ""
end_datetime = ""
if start_date:
    start_datetime = datetime.datetime.combine(start_date, start_time).isoformat()
if end_date:
    end_datetime = datetime.datetime.combine(end_date, end_time).isoformat()
time_input_dict = {
    "start_time": start_datetime,
    "end_time": end_datetime,
    "period_days": days_back,
    "period_hours": hours_back,
}

st.markdown("## Plot")
host = os.getenv("API_HOST")
res = requests.get(
    url=f"http://{host}:80/avg_time/",
    params={**time_input_dict, "frequency": frequency},
)

subset = pd.read_json(StringIO(res.json()))

# TODO: move these calculations to the API

logins = subset[subset["activity_type"] == "login"].reset_index()
logouts = subset[subset["activity_type"] == "logout"].reset_index()
sessions = pd.DataFrame(
    {
        "index_time": logins["time"],
        "login_time": logins["time"],
        "logout_time": logouts["time"],
        "user_id": logins["user_id"],
    }
)

sessions["index_time"] = pd.to_datetime(sessions["index_time"], unit="ms")
sessions["duration"] = sessions["logout_time"] - sessions["login_time"]
sessions = sessions.set_index("index_time")
sessions = sessions.groupby(pd.Grouper(freq=frequency)).mean().reset_index()
sessions["duration"] = sessions["duration"] / (60 * 1000)  # convert from ms to min

df = sessions[["index_time", "duration"]]
min_val = df.loc[:, "duration"].min() * 0.99
max_val = df.loc[:, "duration"].max() * 1.01
line_chart = (
    alt.Chart(df)
    .mark_line()
    .encode(
        x=alt.X("index_time:T", title="Date"),  # Temporal type for timestamps
        y=alt.Y(
            "duration",
            title="Duration (minutes)",
            scale=alt.Scale(domain=[min_val, max_val]),
            axis=alt.Axis(format=",.1f"),
        ),  # axis=alt.Axis(tickCount=int(len(df)/3)))  # Custom y-axis range
    )
)
st.altair_chart(line_chart, use_container_width=True)
st.markdown("## Table")
st.dataframe(df)
