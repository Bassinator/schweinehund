import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# 1. Umgebungsvariablen laden
load_dotenv()

# 2. Systemd-freundliches Logging einrichten
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def main():
    logging.info("Schweinehund launcher tracking app.py environment...")
    
    # Pfade zu den echten Ordnern im Paket ermitteln
    current_dir = Path(__file__).parent.resolve()
    app_path = current_dir / "app.py"
    template_dir = current_dir / "templates"
    static_dir = current_dir / "static"
    
    if not app_path.exists():
        logging.error(f"Critical Error: app.py not found at {app_path}")
        sys.exit(1)
        
    # Lokale Importe innerhalb von app.py absichern
    sys.path.insert(0, str(current_dir))
    
    # 3. FLASK-PFADE KORRIGIEREN (Damit deine app.py unberührt bleibt)
    # Wir überschreiben die Standardpfade, die Flask beim Erstellen nutzt.
    from flask import Flask
    original_init = Flask.__init__
    
    def patched_init(self, *args, **kwargs):
        # Erzwinge die korrekten Pfade aus dem Paketordner
        kwargs['template_folder'] = str(template_dir)
        kwargs['static_folder'] = str(static_dir)
        original_init(self, *args, **kwargs)
        
    # Patch anwenden
    Flask.__init__ = patched_init
    logging.info(f"Flask path injection successful: Templates located at {template_dir}")
    
    # 4. Dynamische Ausführung deiner unveränderten app.py
    try:
        logging.info(f"Booting legacy script via global execution context: {app_path.name}")
        
        with open(app_path, "r", encoding="utf-8") as file:
            code = file.read()
            
        exec(code, {"__name__": "__main__", "__file__": str(app_path)})
        
    except KeyboardInterrupt:
        logging.info("Application shut down gracefully by system interrupt.")
    except Exception as e:
        logging.error(f"Critical execution failure inside app.py: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

