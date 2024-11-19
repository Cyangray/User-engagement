# User-engagement

Python project to provide data analysis and insights from website users, using FastAPI.



# Run

## docker compose

The easiest and most straightforward way to run this is through docker-compose.

First install Docker. You can find instructions on `www.docker.com`. The version used to test this code is docker 27.2.0.

After having installed Docker, you need to create a `.env` file in the root folder of the API with the following content:
 ```
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<db_name>
POSTGRES_PORT=5432
POSTGRES_HOST=postgres
TEST_POSTGRES_USER=test
TEST_POSTGRES_PASSWORD=test
TEST_POSTGRES_DB=test
TEST_POSTGRES_PORT=5432
TEST_POSTGRES_HOST=postgres_test
```
and then run `docker compose up` in your terminal.
The API will then be accessible at `http://0.0.0.0:80/docs` in your browser. To close the API, press command/ctrl+c in the same terminal, and type `docker compose down`.

## Local

To run it locally (not recommended), you should first set up a database container. When this is set up, and you have saved your environment variables in a `.env` file in the root folder, you proceed with the installation guide for the API, and finally run it.


### Database

The database is run with PostgreSQL.

you can download the latest PostgreSQL image by typing

```docker pull postgres```

in your terminal.

You can then build the database image to a docker container. Create an empty `.env` file in the root folder and write
 ```
POSTGRES_HOST=localhost
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<db_name>
```

Then, build your image and run the container by typing the following instructions in the terminal in the same folder

```
docker build -t postgres-img .

docker run -d --name postgres-cont --env-file .env -p 5432:5432 postgres-img
```

If you're already using the 5432 port for something, it might throw an error. You can then try and use another port.
If everything worked, you should be able to see two empty tables called "activities" and "users" in the database. You can do this by typing

```docker exec -it postgres-cont psql -U <username> -d <db_name>```

and then typing

```\dt```

you should obtain something like

```
            List of relations
 Schema |    Name    | Type  |   Owner
--------+------------+-------+-----------
 public | activities | table | <username>
 public | users      | table | <username>
```

### Install API locally

This package was coded using Python3.12.7. Check on https://www.python.org/downloads/ how to install Python on your operative system.

It is easier to install all dependencies with poetry.

First, install poetry with

```pipx install poetry```
(or use `pip` if you want to work in a virtual environment).
The installation was performed with poetry version 1.8.3, and this or later versions should work. If not, one may install precisely this version using

```pipx install poetry==1.8.3```.

Then, go to the main folder, and install all the dependencies using

```poetry install```.

### Run

You run the code locally by typing in a terminal window

```fastapi run src/application.py --port 80```

and then visit `http://0.0.0.0:80/docs` on your browser.
