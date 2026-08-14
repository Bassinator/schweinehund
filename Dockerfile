# 1. Leichtgewichtiges Python-Image als Basis nutzen
FROM python:3.11-slim

# 2. System-Abhängigkeiten für Matplotlib installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Arbeitsverzeichnis im Container definieren
WORKDIR /app

# 4. Anforderungen kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Den gesamten Quellcode und den templates-Ordner kopieren
COPY app.py .
COPY templates/ ./templates/

# 6. Einen Ordner für die persistente Datenbank erstellen
RUN mkdir -p /app/data

# 7. Flask anweisen, die DB im ausgelagerten Datenordner zu suchen
ENV SQLALCHEMY_DATABASE_URI=sqlite:////app/data/todo.db

# 8. Container-Port 8000 öffnen
EXPOSE 8000

# 9. App mit Gunicorn im Produktionsmodus starten (4 Worker für Performance)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]

