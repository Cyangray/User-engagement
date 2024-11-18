FROM ubuntu:latest
LABEL authors="francesco"

ENTRYPOINT ["top", "-b"]


FROM python:3.12


WORKDIR /code


RUN pip install poetry==1.8.3


COPY ./pyproject.toml /code/pyproject.toml


COPY ./poetry.lock /code/poetry.lock


RUN poetry config virtualenvs.create false


RUN poetry install --no-interaction --no-ansi


COPY ./src /code/src
COPY ./tools /code/tools


CMD ["fastapi", "run", "src/application.py", "--port", "80"]
