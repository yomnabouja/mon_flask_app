# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify, g
from flask_mail import Message
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import os
import ollama
from .chatbot import reco_flix_chatbot

# Le Blueprint est défini une seule fois ici
api_routes = Blueprint('api_routes', __name__)

# --- Fonction de connexion à la base de données (corrigée) ---
def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('recoflix.db')
        db.row_factory = sqlite3.Row  # C'est la ligne CRUCIALE qui résout le problème
    return db

# --- Middleware de fermeture de la connexion DB ---
@api_routes.teardown_app_request
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Fonction décoratrice pour les routes d'administration
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session or not session['is_admin']:
            flash('Vous devez être un administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('api_routes.admin_login'))
        return f(*args, **kwargs)
    return decorated_function
    
# --- ROUTES D'ADMINISTRATION (inchangées) ---
@api_routes.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and user['is_admin'] and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['username'] = user['username']
            session['is_admin'] = True
            flash('Connexion administrateur réussie.', 'success')
            return redirect(url_for('api_routes.admin_dashboard'))
        else:
            flash('Identifiants administrateur invalides.', 'danger')
    return render_template('admin_login.html')

@api_routes.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, email, is_admin FROM users').fetchall()
    films = conn.execute('SELECT * FROM films').fetchall()
    return render_template('admin_dashboard.html', users=users, films=films)

@api_routes.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    conn = get_db_connection()
    user_to_delete = conn.execute('SELECT id, is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user_to_delete:
        flash('Utilisateur non trouvé.', 'danger')
        return redirect(url_for('api_routes.admin_dashboard'))
    if user_to_delete['is_admin']:
        flash('Vous ne pouvez pas supprimer un autre administrateur.', 'danger')
        return redirect(url_for('api_routes.admin_dashboard'))
    try:
        conn.execute('DELETE FROM user_films WHERE user_id = ?', (user_id,))
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        flash('Utilisateur supprimé avec succès.', 'success')
    except sqlite3.Error as e:
        flash(f'Erreur lors de la suppression de l\'utilisateur : {e}', 'danger')
    return redirect(url_for('api_routes.admin_dashboard'))
    
@api_routes.route('/admin/add_film', methods=['GET', 'POST'])
@admin_required
def add_film():
    if request.method == 'POST':
        title = request.form.get('title')
        genre = request.form.get('genre')
        description = request.form.get('description')
        rating = request.form.get('rating')
        image_url = request.form.get('image_url')
        video_url = request.form.get('video_url')
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO films (title, genre, description, rating, image_url, video_url) VALUES (?, ?, ?, ?, ?, ?)",
                (title, genre, description, rating, image_url, video_url)
            )
            conn.commit()
            flash('Film ajouté avec succès.', 'success')
            return redirect(url_for('api_routes.admin_dashboard'))
        except sqlite3.Error as e:
            flash(f'Erreur lors de l\'ajout du film : {e}', 'danger')
            return render_template('admin_add_film.html')
    return render_template('admin_add_film.html')

@api_routes.route('/admin/edit_film/<int:film_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_film(film_id):
    conn = get_db_connection()
    film = conn.execute('SELECT * FROM films WHERE id = ?', (film_id,)).fetchone()
    if film is None:
        flash('Film non trouvé.', 'danger')
        return redirect(url_for('api_routes.admin_dashboard'))
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        description = request.form['description']
        rating = request.form['rating']
        image_url = request.form['image_url']
        video_url = request.form['video_url']
        try:
            conn.execute("""
                UPDATE films SET title = ?, genre = ?, description = ?,
                rating = ?, image_url = ?, video_url = ? WHERE id = ?
                """, (title, genre, description, rating, image_url, video_url, film_id))
            conn.commit()
            flash('Film modifié avec succès.', 'success')
            return redirect(url_for('api_routes.admin_dashboard'))
        except sqlite3.Error as e:
            flash(f'Erreur lors de la modification du film : {e}', 'danger')
    return render_template('admin_edit_film.html', film=film)

@api_routes.route('/admin/delete_film/<int:film_id>', methods=['POST'])
@admin_required
def admin_delete_film(film_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM user_films WHERE film_id = ?', (film_id,))
        conn.execute('DELETE FROM films WHERE id = ?', (film_id,))
        conn.commit()
        flash('Film supprimé avec succès.', 'success')
    except sqlite3.Error as e:
        flash(f'Erreur lors de la suppression du film : {e}', 'danger')
    return redirect(url_for('api_routes.admin_dashboard'))

# --- ROUTES UTILISATEURS (inchangées) ---
@api_routes.route('/')
def home():
    return render_template('home.html')

@api_routes.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'] 
        password = request.form['password']
        hashed_password = generate_password_hash(password) 
        conn = get_db_connection()
        try:
            existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
            if existing_user:
                flash('Un utilisateur avec ce nom d\'utilisateur ou cet email existe déjà.', 'warning') 
            else:
                conn.execute('INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, 0)', (username, email, hashed_password))
                conn.commit()
                user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
                session['user_id'] = user_id
                session['email'] = email 
                session['username'] = username 
                session['is_admin'] = False
                flash('Inscription réussie ! Bienvenue sur RecoFlix.', 'success')
                try:
                    if 'mail' in current_app.extensions:
                        msg = Message(
                            subject="Bienvenue sur RecoFlix !",
                            recipients=[email],
                            body=f"Bonjour {username},\n\n"
                                "Nous sommes ravis de vous accueillir sur RecoFlix ! "
                                "Commencez dès maintenant à explorer nos recommandations de films.\n\n"
                                "L'équipe RecoFlix."
                        )
                        current_app.extensions['mail'].send(msg)
                        flash('Un email de bienvenue vous a été envoyé !', 'info')
                except Exception as mail_e:
                    flash(f"Erreur lors de l'envoi de l'email de bienvenue : {mail_e}", 'danger')
                return redirect(url_for('api_routes.dashboard'))
        except sqlite3.IntegrityError:
            flash('Un utilisateur avec ce nom d\'utilisateur ou cet email existe déjà.', 'warning') 
        except Exception as e:
            flash(f'Une erreur inattendue est survenue lors de l\'inscription: {e}', 'danger')
    return render_template('signup.html')

@api_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email_from_form = request.form['email'] 
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (user_email_from_form,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id'] 
            session['email'] = user['email'] 
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            flash(f'Bienvenue {user["username"]} !', 'success')
            return redirect(url_for('api_routes.dashboard')) 
        else:
            flash('Identifiants invalides', 'danger')
    return render_template('login.html')

@api_routes.route('/dashboard')
def dashboard():
    user_id_from_session = session.get('user_id')
    if user_id_from_session: 
        conn = get_db_connection()
        movies = conn.execute('SELECT * FROM films').fetchall()
        favorite_films_query = """
            SELECT f.* FROM films f
            JOIN user_films uf ON f.id = uf.film_id
            WHERE uf.user_id = ?
        """
        favorite_films = conn.execute(favorite_films_query, (user_id_from_session,)).fetchall()
        return render_template('dashboard.html', 
                                user_email=session['email'], 
                                username=session.get('username', 'Utilisateur'),
                                user_id=user_id_from_session,
                                movies=movies,
                                favorite_films=favorite_films,
                                directors=[])
    else:
        flash('Veuillez vous connecter pour accéder au tableau de bord.', 'warning')
        return redirect(url_for('api_routes.login'))

@api_routes.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Déconnecté avec succès', 'info')
    return redirect(url_for('api_routes.login'))

@api_routes.route('/search_films', methods=['GET'])
def search_films():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    conn = get_db_connection()
    try:
        films = conn.execute(
            "SELECT * FROM films WHERE LOWER(title) LIKE LOWER(?)",
            ('%' + query + '%',)
        ).fetchall()
        
        films_list = [dict(film) for film in films]
        return jsonify(films_list)
    except sqlite3.Error as e:
        print(f"Erreur de base de données lors de la recherche: {e}")
        return jsonify({'status': 'error', 'message': 'Erreur interne du serveur'}), 500
    finally:
        conn.close()


@api_routes.route('/get_favorites', methods=['GET'])
def get_favorites():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])
    conn = get_db_connection()
    try:
        favorites = conn.execute("""
            SELECT f.* FROM films f
            JOIN user_films uf ON f.id = uf.film_id
            WHERE uf.user_id = ?
        """, (user_id,)).fetchall()
        favorites_list = [dict(film) for film in favorites]
        return jsonify(favorites_list)
    except sqlite3.Error as e:
        print(f"Erreur de base de données lors du chargement des favoris: {e}")
        return jsonify({'status': 'error', 'message': f'Erreur de la base de données: {e}'}), 500

@api_routes.route('/add_favorite', methods=['POST'])
def add_favorite():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Utilisateur non connecté.'}), 401

    data = request.get_json()
    film_id = data.get('film_id')

    try:
        film_id = int(film_id)
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'ID de film manquant ou invalide.'}), 400

    if not film_id:
        return jsonify({'status': 'error', 'message': 'ID de film manquant ou invalide.'}), 400

    conn = get_db_connection()
    try:
        film = conn.execute('SELECT id FROM films WHERE id = ?', (film_id,)).fetchone()
        if not film:
            return jsonify({'status': 'error', 'message': 'Film non trouvé.'}), 404

        existing_favorite = conn.execute(
            'SELECT 1 FROM user_films WHERE user_id = ? AND film_id = ?',
            (user_id, film_id)
        ).fetchone()

        if existing_favorite:
            return jsonify({'status': 'warning', 'message': 'Film déjà dans les favoris.'}), 409

        conn.execute('INSERT INTO user_films (user_id, film_id) VALUES (?, ?)', (user_id, film_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Film ajouté aux favoris.'}), 200
    
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Erreur lors de l'ajout d'un favori: {e}")
        return jsonify({'status': 'error', 'message': f'Erreur interne du serveur : {e}'}), 500
    
@api_routes.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Utilisateur non connecté.'}), 401

    data = request.json
    film_id = data.get('film_id')
    if not film_id:
        return jsonify({'status': 'error', 'message': 'ID de film manquant.'}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM user_films WHERE user_id = ? AND film_id = ?', 
            (user_id, film_id)
        )
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'status': 'success', 'message': 'Film supprimé des favoris.'})
        else:
            return jsonify({'status': 'error', 'message': 'Film non trouvé dans les favoris.'}), 404
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Erreur lors de la suppression d'un favori: {e}")
        return jsonify({'status': 'error', 'message': f'Erreur lors de la suppression: {e}'}), 500

# --- Routes du Chatbot (inchangées) ---
def chat_with_ollama(prompt, chat_history):
    chat_history.append({"role": "user", "content": prompt})
    try:
        response = ollama.chat(
            model="llama3",
            messages=chat_history
        )
        model_response = response['message']['content'].strip()
        chat_history.append({"role": "assistant", "content": model_response})
        return model_response
    except Exception as e:
        return "Désolé, je n'ai pas pu me connecter à l'assistant. Veuillez vérifier qu'Ollama est bien en cours d'exécution."
        
@api_routes.route('/chat', methods=['POST'])
def chat():
    if request.is_json:
        data = request.get_json()
        user_message = data.get('message')
        if not user_message:
            return jsonify({'response': 'Erreur: message vide'}), 400
        bot_response = reco_flix_chatbot.get_response(user_message)
        return jsonify({'response': bot_response}), 200
    return jsonify({'response': 'Erreur: Type de contenu non supporté'}), 415