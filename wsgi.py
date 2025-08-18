import os
from flask import Flask
from app.routes import api_routes

from app.db import init_app as init_db_app

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'une_cle_secrete_pour_le_dev')

# Configuration mail ici si tu en as

# Enregistre tes blueprints
app.register_blueprint(api_routes)

# Initialise la BDD
init_db_app(app)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
