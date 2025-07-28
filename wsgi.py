import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from app.routes import api_routes # Importation du Blueprint
from app.db import init_app as init_db_app # Importe la fonction init_app de db.py

app = Flask(__name__)

# --- Configuration de la SECRET_KEY (CRUCIAL pour les sessions) ---
app.secret_key = os.environ.get('SECRET_KEY', 'une_cle_secrete_tres_forte_par_defaut_pour_le_dev')

# --- Configuration de Flask-Mail ---
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# --- Enregistrement du Blueprint ---
app.register_blueprint(api_routes)

# --- Initialisation de la base de données avec l'application Flask ---
init_db_app(app) # Appelle la fonction init_app de db.py

# --- Point d'entrée pour le serveur WSGI (Gunicorn) ---
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG') != '0'
    app.run(debug=debug_mode, host='0.0.0.0')
