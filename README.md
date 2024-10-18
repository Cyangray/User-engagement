# User-engagement

Python project to provide data analysis and insights from website users, using FastAPI.

# Install

Copy the repository to your machine, and install the required packages with

```pip install requirements.txt```

# Run

To run it on Docker, go to the main folder and type

```docker build -t myimage```

(the `myimage` image name is to be updated when the project grows)

To run the docker, type

```docker run -d --name mycontainer -p 80:80 myimage```

your container should be running, and at `80:80` you should see the text "Hello, I'm good!".
