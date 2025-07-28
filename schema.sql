DROP TABLE IF EXISTS user_films;
DROP TABLE IF EXISTS films;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE, -- L'email doit être unique et non nul pour une identification correcte
    password TEXT NOT NULL
);

CREATE TABLE films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE, -- Les titres de films doivent être uniques
    genre TEXT,
    description TEXT,
    rating REAL, -- Utiliser REAL pour les évaluations décimales
    image_url TEXT
);

CREATE TABLE user_films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    film_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (film_id) REFERENCES films (id),
    UNIQUE (user_id, film_id) -- Un utilisateur ne peut ajouter un film qu'une seule fois
);
