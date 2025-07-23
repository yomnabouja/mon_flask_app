from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import get_db_connection
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/')
def home():
    # REVERTED: Revenir à la fonction home() d'origine
    return render_template('home.html')

@api_routes.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password) 

        dummy_email = f"{username.lower()}@example.com" 
        email = dummy_email
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Un utilisateur avec ce nom d\'utilisateur ou cet email existe déjà.', 'warning')
            else:
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
                conn.commit()
                flash('Inscription réussie, vous pouvez vous connecter.', 'success')
                conn.close()
                return redirect(url_for('api_routes.login'))
        except sqlite3.IntegrityError as e:
            flash('Erreur lors de l\'inscription (email unique). Veuillez réessayer avec un nom d\'utilisateur différent.', 'danger')
        except Exception as e:
            flash('Une erreur inattendue est survenue lors de l\'inscription.', 'danger')
        finally:
            if conn:
                conn.close()

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
