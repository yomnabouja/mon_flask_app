# Utiliser une image Python officielle
FROM python:3.9-slim

# Copier les fichiers de l'application
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Exposer le port 5000
EXPOSE 5000

# Commande de lancement
CMD ["python", "app.py"]
