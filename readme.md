# 👾 SCHWEINEHUND-BESIEGER 8-BIT RPG v1.0 ⚔️

Ein gamifiziertes To-Do- und Gewohnheits-Tracking-System im unverkennbaren 80s Arcade-Stil. Überwinde deine tägliche Trägheit (den inneren Schweinehund), erledige Quests, sammle XP und knacke den Highscore!

---

## 🕹️ FEATURING
* **Duales Quest-System:** Setze für jede Aufgabe eine minimale Hürde (Etappe 1) und eine Bonus-Herausforderung (Etappe 2).
* **Exklusivitäts-Regel:** Pro Aufgabe und Tag kann nur *entweder* das Minimal-Ziel oder das Bonus-Ziel erreicht werden.
* **Kalender-Historie:** Navigiere durch vergangene Tage, hole verpasste Quests nach oder korrigiere deine Einträge.
* **Retro-Statistiken:** Generiere automatische Highscore-Graphen für Woche, Monat und Jahr.
* **Multi-User & Security:** Sichere Registrierung und verschlüsselte Passwörter via `Werkzeug` und `Flask-Login` mit Case-Sensitive-Schutz.

---

## 💻 1. LOKALE ENTWICKLUNG (DEVELOPMENT)

Um das Projekt lokal weiterzuentwickeln oder anzupassen, folge diesen Schritten:

### Voraussetzungen
Stelle sicher, dass **Python 3.11+** auf deinem System installiert ist.

### Setup ausführen
1. Repository klonen und in den Projektordner wechseln:
   ```bash
   cd meine_schweinehund_app
   ```
2. Virtuelle Umgebung (`venv`) erstellen und aktivieren:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Unter Linux/macOS
   # venv\Scripts\activate   # Unter Windows
   ```
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
4. Die App im Entwicklungsmodus (mit Auto-Reload bei Code-Änderungen) starten:
   ```bash
   python3 app.py
   ```
5. Öffne im Browser: `http://127.0.0`

---

## 🧪 2. TESTEN (TEST DATA GENERATION)

Damit du das Dashboard, den Kalender und vor allem die Graphen nicht mit leeren Händen testen musst, ist ein automatischer **Highscore-Simulator** integriert.

### Testdaten für 1 Jahr simulieren
Führe bei aktiver virtueller Umgebung folgenden Befehl aus:
```bash
python3 generate_test_data.py
```
* Das Skript fragt nach einem **Kriegernamen** (Benutzername).
* **Existiert der User bereits?** Die alten Testdaten dieses Users werden sicher bereinigt und neu ausgewürfelt.
* **Existiert der User noch nicht?** Ein neuer Account wird angelegt (Standard-Passwort: `schweinehund`).
* Anschließend simuliert der Generator realistische, zufällige Erledigungen für die letzten **365 Tage**.

---

## 🚀 3. PROD-HOSTING (PUBLIC INTERNET ACCESS)

Für den echten Einsatz im Internet nutzen wir **Docker** und den produktionsbereiten WSGI-Server **Gunicorn**. Die SQLite-Datenbank wird über ein Volume dauerhaft auf dem Host-Server gespeichert.

### Lokales Docker Image bauen
```bash
docker build -t schweinehund-app:latest .
```

### Deployment auf dem Server (Ohne SSL-Proxy)
Führe diesen Befehl auf deinem Root-Server/VPS aus, um die App im Hintergrund auf Port 80 (HTTP) bereitzustellen:
```bash
docker run -d \
  -p 80:8000 \
  --name schweinehund_game \
  -v /var/lib/schweinehund/data:/app/data \
  --restart unless-stopped \
  schweinehund-app:latest
```

### 🔒 Wichtig für den Live-Betrieb (SSL/HTTPS & Security)
Wenn die App öffentlich im Internet erreichbar ist, **müssen Passwörter verschlüsselt werden**. Über reines HTTP (Port 80) wandern Passwörter im Klartext durchs Netz.

#### Empfohlenes Produktions-Setup (Reverse Proxy):
Schalte einen Reverse Proxy wie **Nginx Proxy Manager**, **Caddy** oder **Traefik** vor deinen Docker-Container. 
1. Starte den Container intern auf einem geschützten Port (z.B. `-p 127.0.0.1:8000:8000`).
2. Lass den Reverse Proxy (Port 80/443) den Traffic entgegennehmen.
3. Der Proxy holt sich via **Let's Encrypt** ein kostenloses SSL-Zertifikat und sorgt für ein sicheres `https://deine-domain.de`.

---

## 📋 4. ARCHITEKTUR & WAS SO ÜBLICH WICHTIG IST

Wenn du das System erweiterst oder im Team entwickelst, beachte folgende Best Practices:

* **Datenbank-Persistenz:** SQLite schreibt alle Daten in eine einzige Datei. Im Dockerfile ist der Pfad fest auf `/app/data/todo.db` verdrahtet. Lösche oder verändere niemals das `-v` (Volume) Argument im `docker run` Befehl, da sonst deine Jahresfortschritte bei jedem Container-Update gelöscht werden!
* **Secret Key:** In der `app.py` findest du `app.config['SECRET_KEY']`. Für die Produktion solltest du diesen Wert unbedingt durch eine zufällige Zeichenkette ersetzen (z. B. generiert via `openssl rand -hex 32`) oder als Umgebungsvariable einbinden.
* **Matplotlib Thread-Safety:** Für die Graphen wird `matplotlib.use('Agg')` verwendet. Dies ist im Web-Kontext zwingend erforderlich, da Matplotlib sonst versucht, ein grafisches Fenster (GUI) auf dem Linux-Server zu öffnen, was zum sofortigen Absturz führt.
* **Datenbank-Migrationen:** Wenn du zukünftig neue Spalten zu `User` oder `Task` hinzufügst, erkennt SQLAlchemy das bei einer bestehenden `todo.db` nicht automatisch. Nutze dafür entweder das Paket `Flask-Migrate` oder lösche die DB (nur im Dev-Modus!), damit sie neu aufgebaut wird.

---

## 🛠️ TECHNOLOGIES USED
* **Backend:** Python, Flask, Flask-SQLAlchemy (SQLite)
* **Auth:** Flask-Login, Werkzeug (Password Hashing)
* **Charts:** Matplotlib (Konvertierung in Base64-Strings für direktes HTML-Rendering)
* **Frontend:** HTML5, CSS3 (Custom CRT-Scanline-Simulation), Google Fonts ("Press Start 2P")

---
**[PLAYER 1 READY]** - Geh raus, besieg deinen Schweinehund und sammle XP! 👾⚔️

