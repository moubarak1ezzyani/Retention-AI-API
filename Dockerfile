# slim : image Python légère
FROM python:3.10-slim

# dossier de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des paquets Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le code source backend + le modèle ML
COPY . .

# Exposition du port 8000 (FastAPI)
EXPOSE 8000

# Commande de lancement (uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]