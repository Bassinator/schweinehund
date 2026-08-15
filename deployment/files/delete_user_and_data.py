import sys

# Sicherer Import aus deinem installierten Paket-Layout
try:
    from schweinehund.app import app, db, User
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    print("❌ Das Paket 'schweinehund' ist nicht in dieser Umgebung installiert.")
    print("Bitte stelle sicher, dass du dich im richtigen Ordner befindest und die venv aktiv ist.")
    sys.exit(1)

def run_user_deletion_ui():
    with app.app_context():
        print("👾 SCHWEINEHUND WARRIOR PURGE TOOL v1.0 ⚔️")
        print("--------------------------------------------")
        
        # 1. Alle registrierten User aus der SQLite-Datenbank auslesen
        users = User.query.order_by(User.id).all()
        
        if not users:
            print("📭 Keine registrierten Krieger in der Datenbank gefunden.")
            return

        print("📋 Registrierte Krieger im System:")
        print(f"{'ID':<6} | {'Kriegername':<20} | {'Aktive Quests':<12}")
        print("-" * 46)
        
        # Mapping-Tabelle für die Auswahl aufbauen
        user_map = {}
        for u in users:
            # Wir lesen die Anzahl der Quests dynamisch über die Beziehung aus
            quest_count = len(u.tasks)
            print(f"{u.id:<6} | {u.username:<20} | {quest_count:<12}")
            user_map[str(u.id)] = u

        print("-" * 46)
        
        # 2. Interaktive Abfrage nach der ID
        selection = input("👉 Gib die ID des Kriegers ein, den du LÖSCHEN möchtest: ").strip()
        
        if selection not in user_map:
            print("❌ Ungültige ID ausgewählt. Vorgang abgebrochen.")
            return

        target_user = user_map[selection]
        
        # 3. Sicherheitsabfrage vor der endgültigen Löschung
        print(f"\n⚠️ ACHTUNG: Du löschst den Krieger '{target_user.username}' (ID: {target_user.id}).")
        print("🔥 Dies löscht UNWIDERRUFLICH den Account, alle Quests, XP und Kalender-Logs!")
        
        confirm = input(f"Bist du absolut sicher? (Tippe exakt 'LÖSCHEN' zum Bestätigen): ").strip()
        
        if confirm != "LÖSCHEN":
            print("❌ Löschvorgang vom Administrator abgebrochen.")
            return

        try:
            print(f"\n💥 Starte kaskadierende Löschung für '{target_user.username}'...")
            
            # Da in deiner app.py die Beziehungen mit cascade="all, delete-orphan" definiert sind,
            # löscht dieser eine Befehl automatisch alle Einträge in task und daily_log mit!
            db.session.delete(target_user)
            db.session.commit()
            
            print("--------------------------------------------")
            print(f"🏆 ERFOLG! Der Krieger '{target_user.username}' wurde vollständig eliminiert.")
            print("Der Name ist ab sofort wieder für ein neues Spiel freigegeben.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Kritischer Datenbankfehler während der Löschtransaktion: {e}")

if __name__ == "__main__":
    run_user_deletion_ui()

