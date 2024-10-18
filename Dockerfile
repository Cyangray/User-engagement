FROM ubuntu:latest
LABEL authors="francesco"

ENTRYPOINT ["top", "-b"]


FROM python:3.12


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./src /code/src


CMD ["fastapi", "run", "src/__main__.py", "--port", "80"]
