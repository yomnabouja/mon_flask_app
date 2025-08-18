import sqlite3
from werkzeug.security import check_password_hash
import os

def get_db_connection():
    # Détecte le chemin de la base de données de manière plus robuste
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(base_dir), 'recoflix.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Récupérer le mot de passe haché depuis la base de données
try:
    conn = get_db_connection()
    user_data = conn.execute('SELECT password FROM users WHERE username = ?', ('admin',)).fetchone()
    conn.close()

    if user_data:
        stored_hashed_password = user_data['password']
        print("Mot de passe haché récupéré de la base de données.")
        
        # Demandez à l'utilisateur de taper le mot de passe qu'il essaie d'utiliser
        test_password = input("Veuillez taper le mot de passe que vous utilisez pour vous connecter : ")
        
        # Vérifiez la correspondance
        if check_password_hash(stored_hashed_password, test_password):
            print("\n✅ SUCCÈS : Le mot de passe correspond.")
            print("Le problème ne vient pas du mot de passe. Le problème est peut-être que la base de données n'a pas été mise à jour.")
        else:
            print("\n❌ ÉCHEC : Le mot de passe NE correspond PAS.")
            print("Le problème est que le mot de passe que vous tapez est incorrect.")
    else:
        print("Utilisateur 'admin' non trouvé dans la base de données. Assurez-vous d'avoir bien exécuté les commandes SQL pour le créer.")

except sqlite3.OperationalError as e:
    print(f"\n❌ ERREUR DE BASE DE DONNÉES : {e}")
    print("Vérifiez que le fichier 'recoflix.db' existe bien et que les tables sont créées.")