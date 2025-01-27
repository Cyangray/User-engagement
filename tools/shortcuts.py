def reset_tables():
    commands = """
                    DROP TABLE IF EXISTS activities;
                    DROP TABLE IF EXISTS users;
                    CREATE TABLE users (
                    user_id INT PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    age SMALLINT,
                    country VARCHAR(2)
                    );
                    CREATE TABLE activities (
                    activity_id UUID PRIMARY KEY,
                    user_id INT REFERENCES users (user_id),
                    time TIMESTAMPTZ,
                    activity_type TEXT,
                    activity_details TEXT
                    );
                    """
    return commands
