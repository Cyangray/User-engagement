FROM ubuntu:latest
LABEL authors="francesco"

ENTRYPOINT ["top", "-b"]

FROM python:3.12 AS base
WORKDIR /code
RUN pip install poetry==1.8.3
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
RUN poetry config virtualenvs.create false


FROM base AS dev
RUN poetry install --no-interaction --no-ansi
COPY . /code
CMD ["fastapi", "run", "src/application.py", "--port", "80"]


# Stage 2: Testing
FROM base AS test
RUN poetry install --no-interaction --no-ansi
COPY . ./code
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-v"]


# Stage 3: Production
FROM base AS prod
RUN poetry install --no-interaction --no-ansi --without test
COPY ./src ./code/src
COPY ./tools ./code/tools
COPY ./.env ./code/.env
CMD ["fastapi", "run", "src/application.py", "--port", "80"]
