from uuid import uuid4
import pandas as pd
import datetime
from fastapi import HTTPException
from pandas.tseries.frequencies import to_offset
from src.models import ActivityTypes


def short_uuid4_generator(bits: int = 30) -> int:
    """
    Small function generating UUID4 short enough to be saved in the SQL database.
    """
    return uuid4().int >> (128 - bits)


def long_uuid4_generator():
    """
    Small function generating a normal UUID4.
    """
    return uuid4()


def filter_time(
    df: pd.DataFrame,
    start_time: str = None,
    end_time: str = None,
    period_days: int = 0,
    period_hours: int = 0,
):
    """
    Helper function to filter a Pandas dataframe with pd.Timestamp objects stored in a column called "time". It will either select the times between a start_time and an end_time, or using an end_time and a time period backwards. If no end_time is selected, "now" is chosen. If no start_time or period is selected, 30 days is chosen as interval.
    :param df: the Pandas dataframe. It must have a column of pd.Timestamps called "time".
    :param start_time: start time (optional) in iso8601 format.
    :param end_time: end time (optional) in iso8601 format.
    :param period_days: time period (optional) in int.
    :param period_hours: time period (optional) in int.
    :return: the filtered dataframe
    """

    assert validate_time_entries(period_days, period_hours, start_time, end_time)

    period = None
    if period_days or period_hours:
        period = datetime.timedelta(days=period_days, hours=period_hours)

    if end_time is None:
        end_time = pd.Timestamp.now(tz="Etc/UTC")
    else:
        end_time = datetime.datetime.fromisoformat(end_time)

    if period and not start_time:
        start_time = end_time - period
    else:
        start_time = datetime.datetime.fromisoformat(start_time)

    return df[(df["time"] > start_time) & (df["time"] <= end_time)]


def polish_activity_types_list(activity_types_input, default):
    """
    Helper function that cleans from None, and validates a list of strings corresponding to the activity types permitted in the ActivityTypes Enum model.
    """

    activity_types = []
    activity_types_input_unique = list(set(activity_types_input))
    activity_types_input_filtered = list(
        filter(lambda x: x is not None, activity_types_input_unique)
    )
    if not activity_types_input_filtered:
        activity_types = default
    else:
        allowed_activities = [
            key for key, _ in ActivityTypes._value2member_map_.items()
        ]
        for activity_type in activity_types_input_filtered:
            if activity_type in allowed_activities:
                activity_types.append(activity_type)
            else:
                raise HTTPException(
                    status_code=400, detail=f"{activity_type}: No such activity type."
                )
    return activity_types


def check_for_allowed_freq_string(string):
    """
    Validating function that checks if the string corresponds to an Offset alias as defined by the Pandas documentation.
    """

    try:
        to_offset(string)
        return True
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid frequency keyword. Please refer to https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases to check on the allowed time frequency strings.",
        )


def validate_timestring(timestring):
    """
    Validating function that checks if the string is in the YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00 format.
    if timestring is None, True is returned
    """
    if timestring:
        try:
            assert ("Z" in timestring) or ("+00:00" in timestring)
            datetime.datetime.fromisoformat(timestring)
            return True
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Wrong datetime string format. It should have the format YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00.",
            )
    else:
        return True


def validate_time_entries(period_days, period_hours, start_time, end_time):
    """
    validating function that checks if the time input for many functions in src.application.py is correct.
    """
    assert validate_timestring(start_time)
    assert validate_timestring(end_time)

    if start_time and (period_days or period_hours):
        raise HTTPException(
            status_code=400,
            detail="Please either provide start_time or period_days/hours, not both.",
        )

    if not start_time and not (period_days or period_hours):
        raise HTTPException(
            status_code=400,
            detail="Neither start_time, period_days or period_hours provided.",
        )
    elif start_time and not (period_days or period_hours):
        return True
    else:
        try:
            assert (period_days > 0) or (period_hours > 0)
            return True
        except AssertionError:
            raise HTTPException(
                status_code=400,
                detail="period_days and period_hours parameters must be positive values.",
            )


def validate_time_bin(time_bin):
    """
    Check if the time string conforms to a set of allowed strings.
    """

    if time_bin in ["month", "day", "hour", "minute", "second"]:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail=f"{time_bin} not a valid time bin to group by. Allowed time bins are 'month', 'day', 'hour', 'minute', 'second'",
        )
