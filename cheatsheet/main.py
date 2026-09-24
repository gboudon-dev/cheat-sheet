import sys
from importlib.resources import files
from pathlib import Path

from PySide6.QtWidgets import QApplication

from cheatsheet.presentation.app_controller import AppController
from cheatsheet.infrastructure.bootstrap import initialize_database
from cheatsheet.infrastructure.database import Database
from cheatsheet.infrastructure.db_manager import DbManager
from cheatsheet.infrastructure.seeder import DataSeeder
from cheatsheet.application.session_manager import SessionManager

def main():
    app = QApplication(sys.argv)
    stylesheet_path = files("cheatsheet.presentation") / "themes" / "modern.qss"
    app.setStyleSheet(stylesheet_path.read_text(encoding="utf-8"))

    package_directory = Path(__file__).resolve().parent
    database = Database(database_url=f"sqlite:///{package_directory.parent / 'cheatsheet.db'}")
    initialize_database(
        database=database,
        seeder=DataSeeder(json_path=files("cheatsheet.infrastructure") / "initial_data.json")
    )
    db_manager = DbManager(session_factory=database.session_factory)
    session_manager = SessionManager(db_manager=db_manager)
    app_controller = AppController(session_manager=session_manager, on_all_windows_closed=app.quit)

    if not app_controller.open_saved_notes():
        note = session_manager.create_note()
        app_controller.open_note_window(note)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()