# User-engagement

Python project to provide data analysis and insights from website users, using FastAPI.

# Install

This package was coded using Python3.12.7. Check on https://www.python.org/downloads/ how to install Python on your operative system.

It is easier to install all dependencies with poetry.

First, install poetry with

```pipx install poetry```
(or use `pip` if you want to work in a virtual environment).
The installation was performed with poetry version 1.8.3, and this or later versions should work. If not, one may install precisely this version using

```pipx install poetry==1.8.3```.

Then, go to the main folder, and install all the dependencies using

```poetry install```.

If using Docker, the version used to test this code is docker 27.2.0.

# Run

To run it locally, you can just type

```fastapi run src/application.py --port 80```

and then visit `http://0.0.0.0:80` on your browser.

## Docker

To run it on Docker, go to the main folder and type

```docker build -t myimage .```

(the `myimage` image name is to be updated when the project grows)

To run the docker, type

```docker run -d --name mycontainer -p 80:80 myimage```

your container should be running, and at `80:80` you should see the text "Hello, I'm good!".

## Database

The database is run with PostgreSQL.

you can download the latest PostgreSQL image by typing

```docker pull postgres```

in your terminal.

You can then build an image. First, go to the User-engagement/db folder, create an empty .env file and write
 ```
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
