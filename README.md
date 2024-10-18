# User-engagement

Python project to provide data analysis and insights from website users, using FastAPI.

# Install

It is easier to install all dependencies with poetry.

First, install poetry with

```pipx install poetry```
(or use `pip` if you want to work in a virtual environment).

Then, go to the main folder, and install all the dependencies using

```poetry install```

# Run

To run it locally, you can just type

```fastapi run src/__main__.py --port 80```

and then visit `http://0.0.0.0:80` on your browser.

## Docker

To run it on Docker, go to the main folder and type

```docker build -t myimage .```

(the `myimage` image name is to be updated when the project grows)

To run the docker, type

```docker run -d --name mycontainer -p 80:80 myimage```

your container should be running, and at `80:80` you should see the text "Hello, I'm good!".
