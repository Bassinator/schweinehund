import sys
import random
from datetime import date, datetime, timedelta

# Importiert deine echten Flask-Komponenten aus dem installierten Paket-Layout
try:
    from schweinehund.app import app, db, User, Task, DailyLog
    from werkzeug.security import generate_password_hash
except ImportError:
    print("❌ Fehler: Das Paket 'schweinehund' ist nicht in der venv installiert.")
    print("Bitte stelle sicher, dass du im richtigen Verzeichnis bist und die venv aktiv ist.")
    print("Führe lokal 'pip install -e .' oder auf dem Server 'pip install .' aus.")
    sys.exit(1)

def run_generator():
    # Wir öffnen den Flask-Anwendungskontext, um Zugriff auf deine todo.db zu haben
    with app.app_context():
        print("👾 SCHWEINEHUND HIGH-SCORE SIMULATOR v2.0 ⚔️")
        print("--------------------------------------------")
        
        # Interaktive Abfrage des Kriegernamens im Terminal
        username = input("👉 Bitte gib den Kriegernamen (Benutzername) ein: ").strip()
        if not username:
            print("❌ Ungültiger Name. Abbruch.")
            return

        # 1. User in deiner Datenbank suchen
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"💥 Krieger '{username}' existiert bereits!")
            print(f"🧹 Überschreibe alte Einträge... Lösche Quests und DailyLogs für {username}...")
            
            # Alte Einträge dieses spezifischen Users löschen (Daten-Reset)
            DailyLog.query.filter_by(user_id=user.id).delete()
            Task.query.filter_by(user_id=user.id).delete()
            db.session.commit()
        else:
            print(f"✨ Neuer Krieger entdeckt! Erstelle Account für '{username}'...")
            # Legt einen neuen User an, falls er nicht existiert (Standard-Passwort: schweinehund)
            hashed_pw = generate_password_hash("schweinehund")
            user = User(username=username, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()

        # 2. Deine originalen Standard-Quests (Tasks) für diesen User anlegen
        print("📜 Schmiede Standard-Quests im Kampfbuch...")
        test_tasks = [
            Task(user_id=user.id, title="🤖 Programmieren / Dev-Session", stage1_text="30 Min Fokus", stage1_points=10, stage2_text="2 Std Deep Work", stage2_points=25),
            Task(user_id=user.id, title="🏋️‍♂️ Krafteinsatz (Sport)", stage1_text="15 Min Dehnen/Liegestütze", stage1_points=5, stage2_text="1 Std Gym/Home-Workout", stage2_points=20),
            Task(user_id=user.id, title="📚 Geistige Nahrung (Lesen)", stage1_text="5 Seiten lesen", stage1_points=5, stage2_text="1 Kapitel studieren", stage2_points=15),
            Task(user_id=user.id, title="💧 Hydration & Vitalität", stage1_text="1.5L Wasser trinken", stage1_points=5, stage2_text="3L Wasser & Clean Eating", stage2_points=15)
        ]
        
        for task in test_tasks:
            db.session.add(task)
        db.session.commit()

        # 3. 365 Tage Historie simulieren (Zufallswerte für die Matplotlib-Graphen)
        print("🔮 Simuliere 365 Tage Highscore-Verlauf. Bitte warten...")
        today = date.today()
        
        for i in range(365):
            current_date = today - timedelta(days=i)
            
            for task in test_tasks:
                rand = random.random()
                # 40% Chance auf Etappe 1 erfüllt
                if rand < 0.40:
                    log = DailyLog(user_id=user.id, task_id=task.id, date=current_date, completed_stage1=True, completed_stage2=False)
                    db.session.add(log)
                # 30% Chance auf Etappe 2 (Bonus) erfüllt
                elif rand < 0.70:
                    log = DailyLog(user_id=user.id, task_id=task.id, date=current_date, completed_stage1=False, completed_stage2=True)
                    db.session.add(log)
                # 30% Chance: Quest an diesem Tag nicht erledigt

            # SQLite-Schutz: Alle 30 Tage ein Zwischen-Commit, um den RAM zu schonen
            if i % 30 == 0:
                db.session.commit()

        # Finaler Datenbank-Sicherungsschritt
        db.session.commit()
        print("--------------------------------------------")
        print(f"🏆 ERFOLG! 365 Tage Testdaten für '{username}' wurden generiert.")
        print("🔐 Das Login-Passwort lautet: 'schweinehund'")

if __name__ == "__main__":
    run_generator()

