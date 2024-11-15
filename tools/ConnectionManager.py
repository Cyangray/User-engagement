from dotenv import dotenv_values
import psycopg

env_values = dotenv_values("db/.env")
db_connection_config = {
    "host": "localhost",
    "dbname": env_values.get("POSTGRES_DB"),
    "user": env_values.get("POSTGRES_USER"),
    "password": env_values.get("POSTGRES_PASSWORD"),
}


class ConnectionManager:
    def __init__(self, connstring: dict):
        self.connection_string = connstring
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg.connect(**self.connection_string, autocommit=True)

        except psycopg.Error as err:
            # sqlstate = err.args[1]
            print(str(err))

    def disconnect(self):
        self.connection.close()


def get_db():
    connection_manager = ConnectionManager(db_connection_config)
    connection_manager.connect()
    return connection_manager
