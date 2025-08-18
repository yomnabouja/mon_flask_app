import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

# ====== Paramètres ======
NEW_PASSWORD = "yomna2002"  # le nouveau mot de passe admin
DB_PATH = os.path.join(os.path.dirname(__file__), "recoflix.db")
# ========================

DB_PATH = r"C:\Users\user\mon_flask_app\recoflix.db"

print(f"📁 Base visée : {DB_PATH}")

# 1) Vérifier que la base existe bien ici
if not os.path.exists(DB_PATH):
    print("❌ ERREUR : 'recoflix.db' introuvable à cet emplacement. "
          "Lance ce script dans le dossier où se trouve réellement ta base.")
    sys.exit(1)

# 2) Ouvrir la base (et vérifier que la table users existe)
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if cur.fetchone() is None:
    print("❌ ERREUR : La table 'users' n'existe pas dans cette base. "
          "Tu n'es probablement pas sur la bonne base recoflix.db.")
    conn.close()
    sys.exit(1)

# 3) Générer le hash et upsert l'admin
hashed = generate_password_hash(NEW_PASSWORD)

cur.execute("SELECT id FROM users WHERE username = ?", ('admin',))
row = cur.fetchone()

if row:
    cur.execute(
        "UPDATE users SET password = ?, is_admin = 1 WHERE username = 'admin'",
        (hashed,)
    )
    action = "mis à jour"
else:
    cur.execute(
        "INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, 1)",
        ('admin', 'admin@example.com', hashed)
    )
    action = "créé"

conn.commit()
conn.close()

print(f"✅ Compte admin {action} avec succès.")
print(f"➡️  Identifiants : username = 'admin'   |   mot de passe = '{NEW_PASSWORD}'")
print("🎯 Tu peux maintenant relancer l'application et te connecter sur /admin.")
