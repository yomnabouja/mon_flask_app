from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app # Ajout de current_app
from flask_mail import Message # Ajout de Message pour l'envoi d'emails
from app.db import get_db_connection
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/')
def home():
    return render_template('home.html')

@api_routes.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'] # CORRECTION ICI : Récupère l'email du formulaire
        password = request.form['password']
        
        hashed_password = generate_password_hash(password) 

        # dummy_email = f"{username.lower()}@example.com" # Cette ligne n'est plus nécessaire
        # email = dummy_email # Cette ligne n'est plus nécessaire
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            print(f"DEBUG (Register): Tentative d'inscription pour username='{username}', email='{email}'")
            cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                print(f"DEBUG (Register): Utilisateur existant trouvé: {existing_user['username']} / {existing_user['email']}")
                # Modification du message flash ici
                flash('Vous avez déjà un compte.', 'warning') 
            else:
                print("DEBUG (Register): Aucun utilisateur existant trouvé, tentative d'insertion...")
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
                conn.commit()
                print("DEBUG (Register): Utilisateur inséré avec succès dans la base de données.")
                
                # --- NOUVEAU : Auto-connexion de l'utilisateur après l'inscription réussie ---
                session['email'] = email
                session['username'] = username 
                print(f"DEBUG (Register): Session['email'] set to: {session['email']}")
                print(f"DEBUG (Register): Session['username'] set to: {session['username']}")

                flash('Inscription réussie ! Bienvenue sur RecoFlix.', 'success')
                
                # --- NOUVEAU : Envoi de l'email de bienvenue après l'inscription ---
                try:
                    msg = Message(
                        subject="Bienvenue sur RecoFlix !",
                        recipients=[email],
                        body=f"Bonjour {username},\n\n"
                             "Nous sommes ravis de vous accueillir sur RecoFlix ! "
                             "Commencez dès maintenant à explorer nos recommandations de films.\n\n"
                             "L'équipe RecoFlix."
                    )
                    # Accède à l'instance de Mail depuis l'application Flask courante
                    current_app.extensions['mail'].send(msg)
                    flash('Un email de bienvenue vous a été envoyé !', 'info')
                    print("DEBUG (Email): Email de bienvenue envoyé avec succès (ou tentative effectuée).")
                except Exception as mail_e:
                    flash(f"Erreur lors de l'envoi de l'email de bienvenue : {mail_e}", 'danger')
                    print(f"DEBUG (Email Error): {mail_e}") # Affiche l'erreur dans les logs du serveur

                conn.close()
                print("DEBUG (Register): Redirection vers le tableau de bord.")
                return redirect(url_for('api_routes.dashboard')) # Redirige directement vers le tableau de bord
        except sqlite3.IntegrityError as e:
            print(f"DEBUG (Register Error): sqlite3.IntegrityError: {e}")
            flash('Erreur lors de l\'inscription (email unique). Veuillez réessayer avec un nom d\'utilisateur différent.', 'danger')
        except Exception as e:
            print(f"DEBUG (Register Error): Erreur inattendue: {e}")
            flash('Une erreur inattendue est survenue lors de l\'inscription.', 'danger')
        finally:
            if conn:
                conn.close()
            print("DEBUG (Register): Connexion à la base de données fermée.")

    print("DEBUG (Register): Rendu de la page signup.html (pas de redirection).")
    return render_template('signup.html')

@api_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email_from_form = request.form['email'] 
        password = request.form['password']

        print(f"DEBUG (Login): Tentative de connexion pour l'email: {user_email_from_form}")
        print(f"DEBUG (Login): Mot de passe saisi: {password}") # ATTENTION: Ne pas faire en production

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (user_email_from_form,))
        user = cursor.fetchone()

        conn.close()

        if user:
            print(f"DEBUG (Login): Utilisateur trouvé: {user['username']}")
            print(f"DEBUG (Login): Mot de passe haché en DB: {user['password']}")
            if check_password_hash(user['password'], password): 
                print("DEBUG (Login): Mot de passe correspond!")
                session['email'] = user['email'] 
                session['username'] = user['username'] 
                print(f"DEBUG (Login): Session['email'] set to: {session['email']}")
                print(f"DEBUG (Login): Session['username'] set to: {session['username']}")
                flash(f'Bienvenue {user["username"]} !', 'success')
                return redirect(url_for('api_routes.dashboard')) 
            else:
                print("DEBUG (Login): Mot de passe ne correspond PAS.")
                flash('Identifiants invalides', 'danger')
        else:
            print("DEBUG (Login): Aucun utilisateur trouvé avec cet email.")
            flash('Identifiants invalides', 'danger')

    return render_template('login.html')

@api_routes.route('/dashboard')
def dashboard():
    print("DEBUG (Dashboard): Accès à la fonction dashboard.")
    print(f"DEBUG (Dashboard): Contenu de la session: {dict(session)}") # Affiche tout le contenu de la session

    if 'email' in session:
        print(f"DEBUG (Dashboard): 'email' trouvé dans la session: {session['email']}")
        print(f"DEBUG (Dashboard): 'username' dans la session: {session.get('username', 'Non défini')}")
        return render_template('dashboard.html', user_email=session['email'], username=session.get('username', 'Utilisateur')) 
    else:
        print("DEBUG (Dashboard): 'email' non trouvé dans la session. Redirection vers la page de connexion.")
        return redirect(url_for('api_routes.login'))

@api_routes.route('/logout')
def logout():
    session.pop('email', None) 
    session.pop('username', None) 
    flash('Déconnecté avec succès', 'info')
    return redirect(url_for('api_routes.login'))
