from dotenv import dotenv_values
import psycopg

import os

env_path = "db/.env"
if os.path.exists(env_path):
    env_values = dotenv_values(env_path)
    env_variables = ["POSTGRES_USER", "POSTGRES_DB", "POSTGRES_PASSWORD"]
    for env_variable in env_variables:
        os.environ[env_variable] = env_values.get(env_variable)

db_connection_config = {
    "host": "localhost",
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


class ConnectionManager:
    def __init__(self, connection_config: dict):
        self.connection_config = connection_config
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg.connect(**self.connection_config, autocommit=True)

        except psycopg.Error as err:
            # sqlstate = err.args[1]
            print(str(err))

    def disconnect(self):
        self.connection.close()


def get_db():
    connection_manager = ConnectionManager(db_connection_config)
    connection_manager.connect()
    return connection_manager
