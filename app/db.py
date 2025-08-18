import sqlite3
import os
from flask import current_app, g
import click
from flask.cli import with_appcontext

# Chemin absolu vers le répertoire racine de l'application Flask
DATABASE_FILE = 'recoflix.db'
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', DATABASE_FILE)

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db_connection()
    cursor = db.cursor()

    # Commandes SQL exécutées directement
    cursor.executescript("""
        -- Supprime les tables existantes
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
            video_url TEXT
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
        VALUES ('yomna', 'yomnaboujelbene1admin@gmail.com', 'scrypt:32768:8:1$uw8eQtLcYR8S5B3N$06598b63f754223c2393e59407db39f12ed29b3afdab7819aab6cb919a0d5f89616861835410a9cd1fb05ceb90679d0c145767028928a4e58ea7a1cbf3c9c297', 1);

        -- Exemple de données de films
        INSERT OR IGNORE INTO films (title, genre, description, rating, image_url, video_url) VALUES
            ('Inception', 'Science-Fiction', 'Un voleur qui dérobe des secrets...', 8.8, 'https://example.com/inception.jpg', 'https://www.youtube.com/embed/Yo1_vI046_M'),
            ('The Matrix', 'Science-Fiction', 'Un programmeur informatique découvre...', 8.7, 'https://example.com/matrix.jpg', 'https://www.youtube.com/embed/m8rrI1lQvD0'),
            ('Parasite', 'Thriller', 'La famille pauvre des Kim s''intéresse à la famille riche des Park...', 8.6, 'https://example.com/parasite.jpg', 'https://www.youtube.com/embed/5xHw-L7o_uA');
    """)

    db.commit()
    print("DEBUG: Base de données initialisée avec le script SQL embarqué.")


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables, then add initial film data."""
    init_db()
    click.echo('Initialized the database and added initial film data.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)