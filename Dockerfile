FROM ubuntu:latest
LABEL authors="francesco"

ENTRYPOINT ["top", "-b"]

FROM python:3.12 AS base
WORKDIR /code
RUN pip install poetry==1.8.3
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
RUN poetry config virtualenvs.create false

# Stage 1: Development
FROM base AS dev
RUN poetry install --no-interaction --no-ansi
COPY src/ /code/src/
COPY tools/ /code/tools/
COPY test/ /code/test/
CMD ["fastapi", "run", "src/application.py", "--port", "80"]


# Stage 2: Testing
FROM base AS test
RUN poetry install --no-interaction --no-ansi
COPY src/ /code/src/
COPY tools/ /code/tools/
COPY test/ /code/test/
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-vs"]


# Stage 3: Production
FROM base AS prod
RUN poetry install --no-interaction --no-ansi --without test
COPY src/ /code/src/
COPY tools/ /code/tools/
CMD ["fastapi", "run", "src/application.py", "--port", "80"]
