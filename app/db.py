import sqlite3
import os
from flask import current_app, g # Importe g pour stocker la connexion à la base de données

# Chemin absolu vers le répertoire racine de l'application Flask
# Cela suppose que db.py est dans app/db.py et que recoflix.db sera à la racine du projet ou dans un dossier 'instance'.
# Pour la simplicité locale, nous allons le placer à la racine du projet.
DATABASE_FILE = 'recoflix.db'
# Utilisez os.path.join pour construire un chemin absolu vers la base de données
# Cela place recoflix.db à la racine du dossier mon_flask_app
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', DATABASE_FILE)

def get_db_connection():
    # Vérifie si la connexion est déjà dans le contexte de l'application Flask (g)
    if 'db' not in g:
        # Si non, établit une nouvelle connexion
        g.db = sqlite3.connect(
            DATABASE_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Configure la connexion pour retourner des lignes sous forme de dictionnaires
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    # Ferme la connexion à la base de données si elle existe dans le contexte de l'application
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    # Ouvre le fichier schema.sql et exécute les commandes SQL
    with current_app.open_resource('schema.sql') as f:
        get_db_connection().executescript(f.read().decode('utf8'))
    print("DEBUG: Base de données initialisée à partir de schema.sql.")

# Fonction pour initialiser l'application Flask avec la base de données
def init_app(app):
    # Enregistre la fonction close_db pour qu'elle soit appelée après chaque requête
    app.teardown_appcontext(close_db)
    # Ajoute une commande 'init-db' à l'interface en ligne de commande de Flask
    app.cli.add_command(init_db_command)

import click
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
