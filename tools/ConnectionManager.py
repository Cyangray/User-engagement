import psycopg
import os
import time
from dotenv import dotenv_values

env_path = ".env"
if os.path.exists(env_path):
    env_values = dotenv_values(env_path)
    env_variables = [
        "POSTGRES_USER",
        "POSTGRES_DB",
        "POSTGRES_PASSWORD",
        "POSTGRES_PORT",
        "POSTGRES_HOST",
    ]
    for env_variable in env_variables:
        os.environ[env_variable] = env_values.get(env_variable)

db_connection_config = {
    "host": os.getenv("POSTGRES_HOST"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "port": os.getenv("POSTGRES_PORT"),
}


class ConnectionManager:
    """
    Class managing the database connection. On initiation, it takes connection details, and the connection is carried out using the connect method. Similarly, the connection is shut down with the disconnect() method.
    """

    def __init__(self, connection_config: dict):
        """
        :param connection_config: dictionary. It should include the keys "host", "dbname", "user" and "password", and the relative values as strings.
        """
        self.connection_config = connection_config
        self.connection = None

    def connect(self):
        """
        Connects to the database using the provided connection parameters.
        """
        # At startup - start connection to the SQL server
        for attempt in range(5):
            try:
                self.connection = psycopg.connect(
                    **self.connection_config, autocommit=True
                )
            except ConnectionError:
                if attempt < 5:
                    print(f"attempt {attempt} failed. Retrying in 5 seconds.")
                    time.sleep(5)
                else:
                    print(
                        "Max number of attempts tried. Connection to the database could not be established."
                    )
                    raise

    def disconnect(self):
        """
        disconnects from the database.
        """
        self.connection.close()


def get_db():
    """Helper function that instantiates the ConnectionManager class, and connects to the database. If db_connection_config is not redefined, it uses the values defined on top of this script."""
    connection_manager = ConnectionManager(db_connection_config)
    connection_manager.connect()
    return connection_manager
