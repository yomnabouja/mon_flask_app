# Utilise une image Python officielle légère comme base
# Assurez-vous que cette version correspond à votre environnement local
FROM python:3.11

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier requirements.txt et installe les dépendances Python
# Cela permet de mettre en cache les couches Docker et d'accélérer les reconstructions
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le reste du code de l'application
COPY . .

# Définit les variables d'environnement pour le mode production et la clé secrète.
# Cette valeur sera écrasée par les paramètres d'application dans Azure.
ENV FLASK_DEBUG=0
ENV SECRET_KEY="une_valeur_par_defaut_locale_pour_le_dev"

# Expose le port sur lequel l'application s'exécutera (Gunicorn par défaut sur 8000)
EXPOSE 8000

# Commande pour exécuter l'application avec Gunicorn
# 'wsgi:app' signifie : dans le fichier 'wsgi.py', trouver l'instance Flask nommée 'app'.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
