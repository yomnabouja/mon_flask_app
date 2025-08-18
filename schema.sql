-- Supprime les tables existantes si elles existent
DROP TABLE IF EXISTS user_films;
DROP TABLE IF EXISTS films;
DROP TABLE IF EXISTS users;

-- Table des utilisateurs
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0
);

-- Table des films
CREATE TABLE films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    genre TEXT,
    description TEXT,
    rating REAL,
    image_url TEXT,
    video_url TEXT,
    watch_url TEXT
);

-- Table de liaison utilisateur-film
CREATE TABLE user_films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    film_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    watched BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (film_id) REFERENCES films (id),
    UNIQUE (user_id, film_id)
);

-- Insertion de l'utilisateur administrateur par défaut
INSERT INTO users (username, email, password, is_admin)
VALUES (
    'admin',
    'admin@recoflix.com',
    '32768:8:1$kmRzoEcmAEv0am3o$e7567ec3c988b137903145997de0e9fe95f21c6496832c19f5e566f3b397d9960d08c325984c873b9d530435554f81eae4115ce518f17b33f926c8971117a36e
    ',
    1
);

INSERT INTO films (title, genre, description, rating, image_url, video_url, watch_url) VALUES 
('Inception', 'Science-Fiction', 'Un voleur qui dérobe des secrets...', 8.8, '/static/css/images/inception.jpg', 'https://www.youtube.com/embed/YoHD9XEInc0', 'https://www.dailymotion.com/video/x8inception'),
('The Matrix', 'Science-Fiction', 'Un programmeur informatique découvre...', 8.7, '/static/css/images/the_matrix.jpg', 'https://www.youtube.com/embed/m8rrI1lQvD0', 'https://www.dailymotion.com/video/x8matrix'),
('Parasite', 'Thriller', 'La famille pauvre des Kim s''intéresse à la famille riche des Park...', 8.6, '/static/css/images/parasite.jpg', 'https://www.youtube.com/embed/5xHw-L7o_uA', 'https://www.dailymotion.com/video/x8parasite'),
('Bayblon', 'Action, Aventure', 'Un film d''action palpitant...', 8.5, '/static/css/images/film1.jpg', 'https://www.youtube.com/watch?v=50P1-oPvZOg', 'https://www.dailymotion.com/video/x8bayblon'),
('Maria Réve', 'Drame, Romance', 'Une histoire d''amour émouvante...', 7.9, '/static/css/images/film2.jpg', 'https://www.youtube.com/watch?v=RbIl4VjibPc', 'https://www.dailymotion.com/video/x9mr95s'),
('Restart', 'Comédie, Famille', 'Une comédie légère et amusante...', 7.2, '/static/css/images/film3.jpg', 'https://www.youtube.com/watch?v=pgq6tjnpMYs', 'https://www.dailymotion.com/video/x9restart'),
('Jumanji', 'Action, Thriller', 'Un film d''action intense...', 8.1, '/static/css/images/film4.jpg', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'https://www.youtube.com/watch?v=RCaOZPZFrG4');
UPDATE films
SET video_url = REPLACE(video_url, 'watch?v=', 'embed/');