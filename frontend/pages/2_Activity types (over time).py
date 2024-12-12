import streamlit as st
import pandas as pd
import datetime
import requests
from io import StringIO

st.title("Activity types (over time)")
st.markdown("## Input values")
st.write(
    "Provide either start date and time, or days/hours back. If end date is not provided, today is chosen by default."
)
col1, col2, col3 = st.columns(3)

# checkbox column for activity types
activity_strings = ["login", "logout", "purchase", "click"]
activity_df = pd.DataFrame(
    {"activity types": activity_strings, "plot": [True, True, True, False]}
)
activity_df = col1.data_editor(
    activity_df,
    column_config={
        "plot": st.column_config.CheckboxColumn(
            "plot", help="plot this activity?", default=False
        )
    },
    disabled=activity_strings,
    hide_index=True,
)
activity_list = []
for i, string in enumerate(activity_strings):
    df = activity_df[activity_df["activity types"] == string]
    val = df["plot"].values[0]
    if val:
        activity_list.append(string)
    else:
        activity_list.append(None)

activity_input_dict = {
    "activity1": activity_list[0],
    "activity2": activity_list[1],
    "activity3": activity_list[2],
    "activity4": activity_list[3],
}

start_date = col2.date_input("start date", None)
start_time = col2.time_input("start time", datetime.time.min)
end_date = col3.date_input("end date", None)
end_time = col3.time_input("end time", datetime.time.max)

col11, col12, col13 = st.columns(3)
days_back = col11.number_input("days back", value=365)
hours_back = col12.number_input("hours back", value=0)
frequency = col13.text_input("frequency", "MS")

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
res = requests.get(
    url="http://0.0.0.0:80/total_activity_over_time/",
    params={**activity_input_dict, **time_input_dict, "frequency": frequency},
)

df = pd.read_json(StringIO(res.json()))
st.bar_chart(data=df, stack=True)
st.markdown("## Table")
st.dataframe(df)
