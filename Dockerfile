# Utiliser une image Python officielle légère
FROM python:3.12-slim

# Installer dépendances système utiles à pandas/numpy
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY Migration_code.py .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Définir la commande par défaut
CMD ["python", "Migration_code.py"]
