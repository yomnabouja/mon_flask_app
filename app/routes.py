from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_mail import Message
from app.db import get_db_connection
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# La ligne suivante était la cause de l'ImportError si elle était présente:
# from app.routes import api_routes # <--- CETTE LIGNE DOIT ÊTRE SUPPRIMÉE SI ELLE EST DANS CE FICHIER

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/')
def home():
    # La route home est maintenant gérée uniquement par le Blueprint
    return render_template('home.html')

@api_routes.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'] # NOUVEAU: Récupère l'email du formulaire
        password = request.form['password']
        
        hashed_password = generate_password_hash(password) 

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
            existing_user = cursor.fetchone()

            print(f"DEBUG (Register): Tentative d'inscription pour username='{username}', email='{email}'")
            if existing_user:
                print(f"DEBUG (Register): Utilisateur existant trouvé: {existing_user['username']} / {existing_user['email']}")
                flash('Un utilisateur avec ce nom d\'utilisateur ou cet email existe déjà.', 'warning')
            else:
                print("DEBUG (Register): Aucun utilisateur existant trouvé, tentative d'insertion...")
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
                conn.commit()
                print("DEBUG (Register): Utilisateur inséré avec succès dans la base de données.")
                
                # --- Auto-connexion de l'utilisateur après l'inscription réussie ---
                session['email'] = email
                session['username'] = username 
                print(f"DEBUG (Register): Session['email'] set to: {session['email']}")
                print(f"DEBUG (Register): Session['username'] set to: {session['username']}")

                flash('Inscription réussie ! Bienvenue sur RecoFlix.', 'success')
                
                # --- Envoi de l'email de bienvenue après l'inscription ---
                try:
                    msg = Message(
                        subject="Bienvenue sur RecoFlix !",
                        recipients=[email], # L'email de l'utilisateur (celui saisi dans le formulaire)
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
            flash(f'Une erreur inattendue est survenue lors de l\'inscription: {e}', 'danger')
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
        # ATTENTION: Ne pas afficher le mot de passe en clair en production
        print(f"DEBUG (Login): Mot de passe saisi: {password}") 

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
    print(f"DEBUG (Dashboard): Contenu de la session: {dict(session)}")

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
