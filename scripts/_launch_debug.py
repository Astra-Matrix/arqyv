"""Step-by-step launch with full error capture printed to console."""
import sys
import traceback

print("Step 1: importing PyQt6...", flush=True)
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

print("Step 2: creating QApplication...", flush=True)
qt_app = QApplication(sys.argv)
qt_app.setApplicationName("ARQYV")

try:
    print("Step 3: loading config...", flush=True)
    from arqyv.config import AppConfig
    config = AppConfig()

    print("Step 4: creating EventBus...", flush=True)
    from arqyv.core.events import EventBus
    events = EventBus()

    print("Step 5: VLC setup...", flush=True)
    from arqyv.media.vlc_setup import setup_vlc
    setup_vlc()

    print("Step 6: initialising database...", flush=True)
    from arqyv.database.db import Database
    import asyncio
    db = Database(url=config.db_url)
    asyncio.run(db.init())

    print("Step 7: building services...", flush=True)
    from arqyv.backend.indexer import Indexer
    from arqyv.search.engine import SearchEngine
    from arqyv.ai.analyzer import AIAnalyzer

    indexer = Indexer(db=db, config=config, events=events)
    search  = SearchEngine(db=db, config=config)
    ai      = AIAnalyzer(config=config, events=events)
    services = {"db": db, "indexer": indexer, "search": search, "ai": ai}

    print("Step 8: opening MainWindow...", flush=True)
    from arqyv.ui.main_window import MainWindow
    window = MainWindow(config=config, events=events, services=services)

    print("Step 9: showing window...", flush=True)
    window.show()
    window.raise_()
    window.activateWindow()

    print("Step 10: entering Qt event loop. Window should be visible now.", flush=True)
    code = qt_app.exec()
    print(f"Qt exited with code {code}", flush=True)
    sys.exit(code)

except Exception:
    err = traceback.format_exc()
    print("\n=== CRASH ===", flush=True)
    print(err, flush=True)

    # Show error in a Qt dialog so it's visible even without a console
    box = QMessageBox()
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle("ARQYV Launch Error")
    box.setText("ARQYV failed to start. See details below.")
    box.setDetailedText(err)
    box.exec()
    sys.exit(1)
