from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from flask_mail import Message
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
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password) 

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            print(f"DEBUG (Register): Tentative d'inscription pour username='{username}', email='{email}'")
            cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                print(f"DEBUG (Register): Utilisateur existant trouvé: {existing_user['username']} / {existing_user['email']}")
                flash('Vous avez déjà un compte.', 'warning') 
            else:
                print("DEBUG (Register): Aucun utilisateur existant trouvé, tentative d'insertion...")
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
                conn.commit()
                user_id = cursor.lastrowid # Récupère l'ID du nouvel utilisateur inséré
                print(f"DEBUG (Register): Utilisateur inséré avec succès dans la base de données. ID: {user_id}")
                
                session['user_id'] = user_id # Stocke l'ID de l'utilisateur dans la session
                session['email'] = email
                session['username'] = username 
                print(f"DEBUG (Register): Session['user_id'] set to: {session['user_id']}")
                print(f"DEBUG (Register): Session['email'] set to: {session['email']}")
                print(f"DEBUG (Register): Session['username'] set to: {session['username']}")

                flash('Inscription réussie ! Bienvenue sur RecoFlix.', 'success')
                
                try:
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
                    print("DEBUG (Email): Email de bienvenue envoyé avec succès (ou tentative effectuée).")
                except Exception as mail_e:
                    flash(f"Erreur lors de l'envoi de l'email de bienvenue : {mail_e}", 'danger')
                    print(f"DEBUG (Email Error): {mail_e}")

                conn.close()
                print("DEBUG (Register): Redirection vers le tableau de bord.")
                return redirect(url_for('api_routes.dashboard'))
        except sqlite3.IntegrityError as e:
            print(f"DEBUG (Register Error): sqlite3.IntegrityError: {e}")
            flash('Un utilisateur avec ce nom d\'utilisateur ou cet email existe déjà.', 'warning') # Message cohérent
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
                session['user_id'] = user['id'] # Stocke l'ID de l'utilisateur dans la session
                session['email'] = user['email'] 
                session['username'] = user['username'] 
                print(f"DEBUG (Login): Session['user_id'] set to: {session['user_id']}")
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

    if 'user_id' in session: # Vérifie l'ID de l'utilisateur dans la session
        print(f"DEBUG (Dashboard): 'user_id' trouvé dans la session: {session['user_id']}")
        print(f"DEBUG (Dashboard): 'email' trouvé dans la session: {session['email']}")
        print(f"DEBUG (Dashboard): 'username' dans la session: {session.get('username', 'Non défini')}")
        return render_template('dashboard.html', 
                               user_email=session['email'], 
                               username=session.get('username', 'Utilisateur'),
                               user_id=session['user_id']) # Passe l'ID de l'utilisateur au template
    else:
        print("DEBUG (Dashboard): 'user_id' non trouvé dans la session. Redirection vers la page de connexion.")
        return redirect(url_for('api_routes.login'))

@api_routes.route('/logout')
def logout():
    session.pop('user_id', None) # Supprime l'ID de l'utilisateur de la session
    session.pop('email', None) 
    session.pop('username', None) 
    flash('Déconnecté avec succès', 'info')
    return redirect(url_for('api_routes.login'))


# --- Add to List Route ---
@api_routes.route('/add_to_list', methods=['POST'])
def add_to_list():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Non authentifié. Veuillez vous connecter.'}), 401

    user_id = session['user_id']
    data = request.get_json()

    # Retrieve all film data, including film_id and video_url
    # film_id might be provided from the frontend if the film already exists in the DB
    film_id_from_frontend = data.get('film_id')
    film_title = data.get('title')
    film_genre = data.get('genre')
    film_description = data.get('description')
    film_rating = data.get('rating')
    film_image = data.get('image')
    film_video_url = data.get('video_url') # <--- Crucial: Get video URL

    if not film_title:
        return jsonify({'status': 'error', 'message': 'Titre du film manquant.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        film_id = None
        # Prioritize looking up by film_id if provided and valid
        if film_id_from_frontend:
            cursor.execute('SELECT id FROM films WHERE id = ?', (film_id_from_frontend,))
            existing_film_by_id = cursor.fetchone()
            if existing_film_by_id:
                film_id = existing_film_by_id['id']
                print(f"DEBUG (AddToList): Film found by ID '{film_id}'.")
            else:
                print(f"DEBUG (AddToList): Film ID '{film_id_from_frontend}' not found, attempting to find by title.")

        # If film_id was not found by its ID, try by title
        if not film_id:
            cursor.execute('SELECT id FROM films WHERE title = ?', (film_title,))
            existing_film_by_title = cursor.fetchone()
            if existing_film_by_title:
                film_id = existing_film_by_title['id']
                print(f"DEBUG (AddToList): Film '{film_title}' already exists with ID: {film_id}")
            else:
                # Insert the film into the 'films' table if it's truly new
                print(f"DEBUG (AddToList): Film '{film_title}' is new, inserting into films table.")
                cursor.execute(
                    'INSERT INTO films (title, genre, description, rating, image_url, video_url) VALUES (?, ?, ?, ?, ?, ?)',
                    (film_title, film_genre, film_description, film_rating, film_image, film_video_url)
                )
                conn.commit()
                film_id = cursor.lastrowid
                print(f"DEBUG (AddToList): Film '{film_title}' inserted with ID: {film_id}")

        # Check if the film is already in the user's list
        cursor.execute('SELECT id FROM user_films WHERE user_id = ? AND film_id = ?', (user_id, film_id))
        user_film_entry = cursor.fetchone()

        if user_film_entry:
            print(f"DEBUG (AddToList): Film '{film_title}' already in user {user_id}'s list.")
            return jsonify({'status': 'info', 'message': 'Ce film est déjà dans votre liste !'}), 200
        else:
            # Add the film to the user's list, 'watched' defaults to 0 (false)
            cursor.execute(
                'INSERT INTO user_films (user_id, film_id, watched) VALUES (?, ?, 0)',
                (user_id, film_id)
            )
            conn.commit()
            print(f"DEBUG (AddToList): Film '{film_title}' added to user {user_id}'s list.")
            return jsonify({'status': 'success', 'message': 'Film ajouté à votre liste avec succès !'}), 200

    except sqlite3.Error as e:
        print(f"DEBUG (AddToList Error): Erreur SQLite: {e}")
        conn.rollback() # Rollback transaction on error
        return jsonify({'status': 'error', 'message': f'Erreur de base de données: {e}'}), 500
    except Exception as e:
        print(f"DEBUG (AddToList Error): Erreur inattendue: {e}")
        return jsonify({'status': 'error', 'message': f'Une erreur inattendue est survenue: {e}'}), 500
    finally:
        if conn:
            conn.close()

# --- Watch Film Route ---
@api_routes.route('/watch/<int:film_id>')
def watch_film(film_id):
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour regarder des films.', 'warning')
        return redirect(url_for('api_routes.login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM films WHERE id = ?', (film_id,))
        film = cursor.fetchone()

        if not film:
            flash('Film introuvable.', 'danger')
            return redirect(url_for('api_routes.dashboard'))

        user_id = session['user_id']
        # Mark the film as "watched" in the user's list if it's there
        # This UPDATE only affects existing entries
        cursor.execute(
            'UPDATE user_films SET watched = 1 WHERE user_id = ? AND film_id = ?',
            (user_id, film_id)
        )
        conn.commit()
        print(f"DEBUG (WatchFilm): Film '{film['title']}' marked as watched for user {user_id}.")

        return render_template('watch_film.html', film=film)

    except sqlite3.Error as e:
        print(f"DEBUG (WatchFilm Error): Erreur SQLite: {e}")
        flash(f'Une erreur de base de données est survenue: {e}', 'danger')
        return redirect(url_for('api_routes.dashboard'))
    except Exception as e:
        print(f"DEBUG (WatchFilm Error): Erreur inattendue: {e}")
        flash(f'Une erreur inattendue est survenue lors de la lecture du film: {e}', 'danger')
        return redirect(url_for('api_routes.dashboard'))
    finally:
        if conn:
            conn.close()

# --- My List Route ---
@api_routes.route('/my_list')
def my_list():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour voir votre liste.', 'warning')
        return redirect(url_for('api_routes.login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch films from the user's list, along with their 'watched' status
        cursor.execute(
            '''
            SELECT f.id, f.title, f.genre, f.description, f.rating, f.image_url, f.video_url, uf.watched
            FROM user_films uf
            JOIN films f ON uf.film_id = f.id
            WHERE uf.user_id = ?
            ORDER BY uf.added_at DESC
            ''',
            (user_id,)
        )
        my_films = cursor.fetchall()
        print(f"DEBUG (MyList): {len(my_films)} films trouvés pour l'utilisateur {user_id}.")

        return render_template('my_list.html', my_films=my_films)

    except sqlite3.Error as e:
        print(f"DEBUG (MyList Error): Erreur SQLite: {e}")
        flash(f'Une erreur de base de données est survenue: {e}', 'danger')
        return redirect(url_for('api_routes.dashboard'))
    except Exception as e:
        print(f"DEBUG (MyList Error): Erreur inattendue: {e}")
        flash(f'Une erreur inattendue est survenue lors de la récupération de votre liste: {e}', 'danger')
        return redirect(url_for('api_routes.dashboard'))
    finally:
        if conn:
            conn.close()

# --- Remove From List Route ---
@api_routes.route('/remove_from_list', methods=['POST'])
def remove_from_list():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Non authentifié. Veuillez vous connecter.'}), 401

    user_id = session['user_id']
    data = request.get_json()
    film_id = data.get('film_id')

    if not film_id:
        return jsonify({'status': 'error', 'message': 'ID du film manquant.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'DELETE FROM user_films WHERE user_id = ? AND film_id = ?',
            (user_id, film_id)
        )
        conn.commit()

        if cursor.rowcount > 0:
            print(f"DEBUG (RemoveFromList): Film {film_id} retiré de la liste de l'utilisateur {user_id}.")
            return jsonify({'status': 'success', 'message': 'Film retiré de votre liste.'}), 200
        else:
            print(f"DEBUG (RemoveFromList): Film {film_id} non trouvé dans la liste de l'utilisateur {user_id}.")
            return jsonify({'status': 'info', 'message': 'Ce film n\'est pas dans votre liste.'}), 200

    except sqlite3.Error as e:
        print(f"DEBUG (RemoveFromList Error): Erreur SQLite: {e}")
        conn.rollback()
        return jsonify({'status': 'error', 'message': f'Erreur de base de données: {e}'}), 500
    except Exception as e:
        print(f"DEBUG (RemoveFromList Error): Erreur inattendue: {e}")
        return jsonify({'status': 'error', 'message': f'Une erreur inattendue est survenue: {e}'}), 500
    finally:
        if conn:
            conn.close()
