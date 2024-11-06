CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age SMALLINT,
    country VARCHAR(2)
);

CREATE TABLE activities (
    activity_id INT PRIMARY KEY,
    user_id INT,
    time TIMESTAMPTZ,
    activity_type TEXT,
    activity_details TEXT
);
