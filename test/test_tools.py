import pytest

from tools.tools import (
    filter_time,
    polish_activity_types_list,
    check_for_allowed_freq_string,
    validate_timestring,
    validate_time_entries,
    validate_time_bin,
)


def test_filter_time_start_end(mock_dataframe):
    start_time = "2020-04-23T13:00:01Z"
    end_time = "2020-04-23T15:00:01Z"
    period_days = 0
    period_hours = 0
    df = filter_time(mock_dataframe, start_time, end_time, period_days, period_hours)
    assert len(df) == 1


def test_filter_time_period_end(mock_dataframe):
    start_time = None
    period_days = 0
    period_hours = 3
    end_time = "2020-04-23T16:00:02Z"
    df = filter_time(mock_dataframe, start_time, end_time, period_days, period_hours)
    assert len(df) == 2


def test_polish_activity_types_list():
    default = ["login", "logout", "click"]
    lists_to_test = [
        [None, None, None, None],
        ["purchase", None, None, None],
        [None, "login", None, None],
        [None, None, "logout", None],
        [None, None, None, "click"],
        ["login", "logout"],
        ["login", "logout", "click", "purchase"],
        ["click", "click", "click", "click"],
    ]
    expected_results = [
        default,
        ["purchase"],
        ["login"],
        ["logout"],
        ["click"],
        ["login", "logout"],
        ["login", "logout", "click", "purchase"],
        ["click"],
    ]

    for list_to_test, expected_result in zip(lists_to_test, expected_results):
        assert set(expected_result) == set(
            polish_activity_types_list(list_to_test, default)
        )


@pytest.mark.parametrize(
    "list_to_test",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [["Login"], [33], ["Pippo"]]
    ],
)
def test_invalid_activity_types_list(list_to_test):
    default = ["login", "logout", "click"]
    polish_activity_types_list(list_to_test, default)


def test_check_for_allowed_freq_string():
    strings_to_test = [
        "B",
        "C",
        "D",
        "W",
        "ME",
        "SME",
        "CBME",
        "MS",
        "QS",
        "YS",
        "h",
        "bh",
        "min",
        "s",
        "1h30min",
        "3D4h33min",
    ]
    for string_to_test in strings_to_test:
        assert check_for_allowed_freq_string(string_to_test)


@pytest.mark.parametrize(
    "string_to_test",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in ["Login", 33, "Pippo", "hour", "day", "year"]
    ],
)
def test_invalid_check_for_allowed_freq_string(string_to_test):
    check_for_allowed_freq_string(string_to_test)


def test_validate_timestring():
    timestrings = ["2020-04-23T16:00:01Z", "2020-04-23T16:00:01+00:00"]
    for timestring in timestrings:
        assert validate_timestring(timestring)


@pytest.mark.parametrize(
    "timestring",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [
            "Login",
            33,
            "Pippo",
            "hour",
            "20-04-23T16:00:01Z",
            "2020-04-23T16:00:01S",
            "2020-04-23T16:00:01",
        ]
    ],
)
def test_invalid_timestring(timestring):
    validate_timestring(timestring)


def test_validate_time_entries():
    valid_input_lists = [
        [0, 0, "2020-04-23T16:00:01Z", None],
        [1, 0, None, None],
        [1, 1, None, None],
        [0, 1, None, None],
    ]
    for valid_input_list in valid_input_lists:
        period_days, period_hours, start_time, end_time = valid_input_list
        assert validate_time_entries(period_days, period_hours, start_time, end_time)


@pytest.mark.parametrize(
    "input_list",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in [
            [0, 0, None, None],
            [1, 0, "2020-04-23T16:00:01Z", None],
            [0, 1, "2020-04-23T16:00:01Z", None],
            [1, 1, "2020-04-23T16:00:01Z", None],
            [-1, 0, None, None],
            [0, -1, None, None],
            ["pippo", 4, None, None],
            [0, 0, "2020-04-23T16:00:01S", None],
        ]
    ],
)
def test_invalid_time_entries(input_list):
    period_days, period_hours, start_time, end_time = input_list
    assert validate_time_entries(period_days, period_hours, start_time, end_time)


def test_validate_time_bin():
    strings = ["month", "day", "hour", "minute", "second"]
    for string in strings:
        assert validate_time_bin(string)


@pytest.mark.parametrize(
    "string",
    [
        pytest.param(item, marks=pytest.mark.xfail)
        for item in ["Month", "D", "M", "MS", "m", "Pippo", 33, -4, None]
    ],
)
def test_invalid_time_bins(string):
    validate_time_bin(string)
