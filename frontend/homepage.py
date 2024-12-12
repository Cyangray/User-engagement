import streamlit as st
import requests

st.title("User Engagement Dashboard")

st.markdown("""
User Engagement is a project ideated by [Ana Budiša](https://github.com/anabudisa) and coded by [Francesco Pogliano](https://github.com/Cyangray/).

The aim of the project is to learn and use useful features of Python such as Poetry, Pytest, FastAPI, Pydantic, Pandas,
Streamlit, and other tools such as PostgreSQL, Docker, docker-compose, networking, GitHub and CI.

The idea behind the project, is the tracking of user behaviour in a hypothetical website, where the user may do the actions
"login", "click", "purchase" and "logout". The data is channeled through an API and saved to a PostgreSQL database. When
This dashboard requires it, the data is retrieved by the API, processed and given to this frontend, where can be plotted
in four plots, available in the sidebar.

The repository of the project, with more information on how to install and use it, can be found on [GitHub](https://github.com/Cyangray/User-engagement).

### The dataset
The data plotted here is script-generated, simple but realistic. You can generate it by adjusting
the parameters here, and clicking on "generate". You can do this as many times as you want, and the new dataset will replace
the previous one. It may take some time, depending on how much data you decided to create and write to the database!
""")

col1, col2, col3, col4 = st.columns(4)

n_users = col1.number_input("number of users", 1, value=20)
clicks_per_minute = col2.number_input("clicks per minute", 1, value=1)
session_length_hours = col3.number_input("session length (hours)", 1, value=2)
sessions_per_year = col4.number_input("sessions per year", 1, value=10)

input_dict = {
    "n_users": n_users,
    "clicks_per_minute": clicks_per_minute,
    "session_length_hours": session_length_hours,
    "sessions_per_year": sessions_per_year,
}
if st.button("regenerate"):
    res = requests.post(url="http://0.0.0.0:80/regen_dataset/", params=input_dict)

    if res.status_code == 200:
        st.write("Data generated!")
