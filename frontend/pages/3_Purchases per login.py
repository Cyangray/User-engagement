import os

import streamlit as st
import pandas as pd
import datetime
import requests
from io import StringIO

st.title("Purchases per login")
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
try:
    host = os.getenv("API_HOST")
    res = requests.get(
        url=f"http://{host}:80/purchases/",
        params={**time_input_dict, "frequency": frequency},
    )

    df = pd.read_json(StringIO(res.json()))
    st.line_chart(data=df.loc[:, ["avg_purchases_per_login"]])
    st.markdown("## Table")
    st.dataframe(df.loc[:, ["avg_purchases_per_login"]])
except requests.exceptions.JSONDecodeError:
    st.write(
        'No data found to plot. The criteria might be too narrow, or there might be no data in the database. Have you clicked on "regenerate" in the homepage?'
    )
