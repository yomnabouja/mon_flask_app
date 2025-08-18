import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('../recoflix.db')  # ajuste le chemin si nécessaire
cursor = conn.cursor()

# Requête pour afficher tous les titres de films
try:
    cursor.execute("SELECT id, title FROM films")
    films = cursor.fetchall()
    print("Liste des films dans la base de données :")
    for film in films:
        print(f"{film[0]} - {film[1]}")
except sqlite3.Error as e:
    print("Erreur SQL :", e)

conn.close()
