import random
from datetime import date, timedelta
from werkzeug.security import generate_password_hash
from app import db, app, User, Task, DailyLog

with app.app_context():
    print("=== MULTI-USER TESTDATEN GENERATOR ===")
    target_username = input("Für welchen Benutzernamen sollen Daten generiert werden?: ").strip()
    
    if not target_username:
        print("Fehler: Kein Benutzername eingegeben. Vorgang abgebrochen.")
        exit()

    # 1. Benutzer suchen oder neu anlegen
    user = User.query.filter_by(username=target_username).first()
    
    if user:
        print(f"-> Benutzer '{target_username}' gefunden.")
        # Bereinige nur die Daten DIESES Benutzers
        DailyLog.query.filter_by(user_id=user.id).delete()
        Task.query.filter_by(user_id=user.id).delete()
        print(f"-> Bestehende Aufgaben und Logs für '{target_username}' wurden gelöscht.")
    else:
        print(f"-> Benutzer '{target_username}' existiert noch nicht. Wird neu angelegt...")
        # Generiert einen Account. Passwort ist standardmäßig 'schweinehund'
        hashed_pw = generate_password_hash("schweinehund")
        user = User(username=target_username, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        print(f"-> Account '{target_username}' erstellt (Passwort: schweinehund).")

    # 2. Beispiel-Aufgaben exklusiv für diesen Benutzer anlegen
    t1 = Task(user_id=user.id, title="Laufen", stage1_text="3 km", stage1_points=15, stage2_text="8 km", stage2_points=40)
    t2 = Task(user_id=user.id, title="Klimmzüge", stage1_text="5 Stück", stage1_points=10, stage2_text="15 Stück", stage2_points=30)
    t3 = Task(user_id=user.id, title="Programmieren", stage1_text="15 Min", stage1_points=10, stage2_text="60 Min", stage2_points=35)
    
    db.session.add_all([t1, t2, t3])
    db.session.commit()
    
    tasks = [t1, t2, t3]
    today = date.today()
    print("Generiere Testdaten für 365 Tage...")
    
    # 3. Testdaten für 365 Tage generieren
    for i in range(365):
        current_date = today - timedelta(days=i)
        for task in tasks:
            rand = random.random()
            # Einhaltung der Exklusivitäts-Regel: entweder s1 oder s2
            if rand < 0.4:
                log = DailyLog(user_id=user.id, task_id=task.id, date=current_date, completed_stage1=True, completed_stage2=False)
                db.session.add(log)
            elif rand < 0.7:
                log = DailyLog(user_id=user.id, task_id=task.id, date=current_date, completed_stage1=False, completed_stage2=True)
                db.session.add(log)

    db.session.commit()
    print(f"\nErfolgreich 1 Jahr Testdaten für den User '{target_username}' generiert!")

