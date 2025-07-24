import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message # Importation de Flask-Mail

app = Flask(__name__)

# --- Configuration de Flask-Mail ---
# Ces variables doivent être définies comme variables d'environnement
# sur votre machine locale et sur Azure App Service.
# Exemple pour Azure App Service :
# az webapp config appsettings set --name recoflix-app-yomna --resource-group RecoFlixResourceGroup --settings MAIL_SERVER="smtp.gmail.com" MAIL_PORT="587" MAIL_USE_TLS="True" MAIL_USERNAME="votre_email@gmail.com" MAIL_PASSWORD="votre_mot_de_passe_app_gmail" MAIL_DEFAULT_SENDER="votre_email@gmail.com"
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com') # Ex: smtp.gmail.com pour Gmail
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587)) # Ex: 587 pour TLS, 465 pour SSL
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# --- Configuration existante de l'application ---
app.secret_key = os.environ.get('SECRET_KEY', 'une_cle_secrete_tres_forte_par_defaut_pour_le_dev')
# Assurez-vous que SECRET_KEY est bien défini dans les variables d'environnement Azure

# --- Routes et logique de l'application ---

# Exemple de route d'accueil
@app.route('/')
def home():
    if 'email' in session:
        return render_template('dashboard.html', user_email=session['email'])
    return render_template('home.html') # Ou rediriger vers la page de login

# Route de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # --- Logique de vérification des identifiants (à implémenter) ---
        # Ici, vous devriez vérifier l'email et le mot de passe dans votre base de données.
        # Pour l'exemple, nous allons simuler une connexion réussie.
        if email == "test@gmail.com" and password == "password123": # REMPLACER PAR VOTRE VRAIE LOGIQUE
            session['email'] = email
            flash('Connexion réussie !', 'success')

            # --- Envoi de l'email de bienvenue après connexion réussie ---
            try:
                msg = Message(
                    subject="Bienvenue sur RecoFlix !",
                    recipients=[email],
                    body=f"Bonjour {email},\n\n"
                         "Nous sommes ravis de vous accueillir sur RecoFlix ! "
                         "Vous avez un compte et vous êtes les bienvenus.\n\n"
                         "Commencez dès maintenant à explorer nos recommandations de films.\n\n"
                         "L'équipe RecoFlix."
                )
                mail.send(msg)
                flash('Un email de bienvenue vous a été envoyé !', 'info')
            except Exception as e:
                flash(f"Erreur lors de l'envoi de l'email de bienvenue : {e}", 'danger')
                print(f"Erreur d'envoi d'email: {e}") # Pour le débogage dans les logs

            return redirect(url_for('dashboard')) # Rediriger vers le tableau de bord
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    return render_template('login.html')

# Route d'inscription (exemple, à adapter si vous en avez une)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Ici, vous ajouteriez la logique pour créer un nouvel utilisateur dans votre base de données
        # et gérer les erreurs (email déjà pris, mot de passe faible, etc.)
        flash('Inscription réussie ! Veuillez vous connecter.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html') # Assurez-vous d'avoir un template signup.html

# Route de déconnexion
@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('home'))

# Route du tableau de bord (exemple)
@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        flash('Veuillez vous connecter pour accéder au tableau de bord.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_email=session['email'])

# Assurez-vous que cette partie est présente pour que Gunicorn puisse trouver l'application
if __name__ == '__main__':
    app.run(debug=True)
