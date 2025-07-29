import sqlite3
import os
from flask import current_app, g # Importe g pour stocker la connexion à la base de données
import click
from flask.cli import with_appcontext

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
    db = get_db_connection() # Obtenez la connexion à la base de données
    
    # 1. Exécute le schema.sql pour créer les tables
    # Assurez-vous que votre schema.sql est bien celui que vous avez fourni,
    # avec les colonnes 'title', 'genre', 'description', 'rating', 'image_url', 'video_url' pour la table 'films'.
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    print("DEBUG: Base de données initialisée à partir de schema.sql.")

    # 2. Ajout des données initiales pour les films
    # La liste des films doit maintenant correspondre aux colonnes de la table 'films' dans votre schema.sql
    # L'ordre des éléments dans chaque tuple doit être:
    # (title, genre, description, rating, image_url, video_url)
    films_a_ajouter = [
        ("Le Voyage de Chihiro", "Animation, Fantastique, Aventure", "Chihiro, une jeune fille de 10 ans, déménage avec ses parents. Sur la route, ils s'arrêtent devant un mystérieux tunnel qui les mène vers un monde peuplé de dieux et d'esprits. Un chef-d'œuvre de l'animation japonaise.", 9.0, "css/images/voyage1.jpg", "https://www.youtube.com/embed/ByXuk9Qqxkk"),
        ("Film Populaire 1", "Action, Aventure", "Un film d'action palpitant avec des scènes spectaculaires et une histoire captivante.", 8.5, "css/images/film1.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Film Populaire 2", "Drame, Romance", "Une histoire d'amour émouvante et déchirante qui vous tiendra en haleine du début à la fin.", 7.9, "css/images/film2.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Film Populaire 3", "Science-fiction, Thriller", "Un thriller de science-fiction qui explore les limites de la technologie et de l'humanité.", 8.8, "css/images/film3.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Film Populaire 4", "Comédie, Famille", "Une comédie légère et amusante parfaite pour toute la famille, pleine de rires et de moments tendres.", 7.2, "css/images/film4.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Film Populaire 5", "Action, Thriller", "Un film d'action intense avec des rebondissements inattendus et une performance d'acteur exceptionnelle.", 8.1, "css/images/film5.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Film Populaire 6", "Animation, Aventure", "Une aventure animée pleine de magie et de personnages attachants, pour petits et grands.", 8.3, "css/images/vu film1.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Film Populaire 7", "Fantastique, Drame", "Un drame fantastique qui explore des thèmes profonds avec une touche de surnaturel.", 7.5, "css/images/vu film2.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Film Populaire 8", "Comédie, Musical", "Une comédie musicale entraînante avec des numéros de danse et des chansons mémorables.", 7.8, "css/images/vu film3.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Film Populaire 9", "Horreur, Mystère", "Un film d'horreur psychologique qui vous tiendra en haleine jusqu'à la dernière minute.", 6.9, "css/images/tendance1.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Film Populaire 10", "Action, Aventure", "Une aventure épique remplie d'action, de trésors cachés et de paysages à couper le souffle.", 8.0, "css/images/tendance2.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Vaiana 2", "Animation, Aventure", "Une suite captivante avec de nouveaux défis et des personnages inoubliables.", 7.8, "css/images/vu film1.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Le Roi Lion", "Animation, Drame", "Le Roi Lion est un classique intemporel de Disney. Suivez l'histoire de Simba.", 9.0, "css/images/le roi lion.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Interstellar", "Science-fiction, Drame", "Un groupe d'explorateurs interstellaires utilise un trou de ver pour échapper à un futur où la Terre est mourante.", 8.6, "css/images/tendance3.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("Inception", "Science-fiction, Action", "Un voleur qui dérobe des secrets d'entreprise en utilisant la technologie de partage de rêves est chargé d'une mission inverse.", 8.8, "css/images/inception.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("La La Land", "Musical, Romance, Drame", "Un musicien de jazz et une actrice en herbe tombent amoureux à Los Angeles.", 7.9, "css/images/La la land.jpg", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
    ]

    cursor = db.cursor() # Obtenez un curseur pour exécuter les requêtes
    for title, genre, description, rating, image_url, video_url in films_a_ajouter:
        try:
            # La requête SQL INSERT OR REPLACE est maintenant parfaitement alignée avec votre schema.sql
            # en utilisant les colonnes: title, genre, description, rating, image_url, video_url
            cursor.execute(
                "INSERT OR REPLACE INTO films (title, genre, description, rating, image_url, video_url) VALUES (?, ?, ?, ?, ?, ?)",
                (title, genre, description, rating, image_url, video_url)
            )
            # print(f"DEBUG: Film '{title}' ajouté/mis à jour.") # Décommentez pour plus de détails lors de l'exécution
        except sqlite3.IntegrityError:
            # Cette erreur est moins probable avec INSERT OR REPLACE, mais gardée pour la robustesse
            print(f"ATTENTION: Le film '{title}' existe déjà et n'a pas été mis à jour (IntegrityError).")
        except Exception as e:
            print(f"ERREUR: Lors de l'ajout de '{title}': {e}")
    
    db.commit() # Valider les changements après l'ajout de tous les films
    print("DEBUG: Données initiales des films ajoutées/mises à jour.")


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables, then add initial film data."""
    init_db()
    click.echo('Initialized the database and added initial film data.')

# Fonction pour initialiser l'application Flask avec la base de données
def init_app(app):
    # Enregistre la fonction close_db pour qu'elle soit appelée après chaque requête
    app.teardown_appcontext(close_db)
    # Ajoute une commande 'init-db' à l'interface en ligne de commande de Flask
    app.cli.add_command(init_db_command)

