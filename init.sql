CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    age SMALLINT,
    country VARCHAR(2)
);

CREATE TABLE IF NOT EXISTS activities (
    activity_id INT PRIMARY KEY,
    user_id INT REFERENCES users (user_id),
    time TIMESTAMPTZ,
    activity_type TEXT,
    activity_details TEXT
);
