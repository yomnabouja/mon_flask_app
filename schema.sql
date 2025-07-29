-- schema.sql

-- Supprime les tables existantes si elles existent, pour un démarrage propre
-- C'est important pour appliquer les nouvelles structures de table
DROP TABLE IF EXISTS user_films;
DROP TABLE IF EXISTS films;
DROP TABLE IF EXISTS users;

-- Table des utilisateurs
-- Stocke les informations de chaque utilisateur enregistré
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE, -- L'email doit être unique et non nul pour une identification correcte
    password TEXT NOT NULL
);

-- Table des films
-- Stocke les détails de chaque film que l'application peut recommander ou afficher
CREATE TABLE films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE, -- Le titre du film, doit être unique
    genre TEXT,                 -- Le genre du film (ex: "Action, Aventure")
    description TEXT,           -- Une brève description du film
    rating REAL,                -- L'évaluation du film (nombre décimal, ex: 8.5)
    image_url TEXT,             -- Le chemin de l'image de la jaquette du film (ex: "css/images/film1.jpg")
    video_url TEXT              -- L'URL d'intégration (embed) de la bande-annonce (ex: "https://www.youtube.com/embed/...")
);

-- Table de liaison utilisateur-film (pour la liste de l'utilisateur)
-- Permet de savoir quels films un utilisateur a ajoutés à sa liste ou regardés
CREATE TABLE user_films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    film_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Date et heure d'ajout à la liste
    watched BOOLEAN DEFAULT 0,                   -- Indique si le film a été marqué comme "vu" (0 pour non, 1 pour oui)
    FOREIGN KEY (user_id) REFERENCES users (id), -- Lien vers la table 'users'
    FOREIGN KEY (film_id) REFERENCES films (id), -- Lien vers la table 'films'
    UNIQUE (user_id, film_id)                   -- Un utilisateur ne peut ajouter le même film qu'une seule fois
);
