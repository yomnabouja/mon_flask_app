DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    -- Email is now nullable and not unique, which is problematic for login/user identification
    email TEXT, 
    password TEXT NOT NULL
);
