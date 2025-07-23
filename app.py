from flask import Flask
from app.routes import api_routes # Assurez-vous que ce chemin est correct.
                                  # Si 'app.py' est à la racine et 'routes.py' est dans le dossier 'app',
                                  # alors 'from app.routes import api_routes' est correct.

app = Flask(__name__)
# IMPORTANT : Remplacez 'your_super_secret_key_here' par une longue chaîne de caractères aléatoires et complexe.
# C'est essentiel pour la sécurité des sessions Flask et des messages flash.
# Vous pouvez générer une clé avec os.urandom(24).hex()
app.config['SECRET_KEY'] = 'a96683f94638ccf1947210479b1d6b53c4fb1c32e7a1d1d3' 

# Enregistrez votre Blueprint
app.register_blueprint(api_routes)

if __name__ == '__main__':
    # Activez le mode débogage pour le développement.
    # Désactivez-le en production (debug=False).
    # 'host='0.0.0.0'' permet d'accéder à l'application depuis d'autres machines sur le réseau local.
    app.run(debug=True, host='0.0.0.0') 