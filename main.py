import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app_controller import AppController
from bootstrap import initialize_database
from database import Database
from db_manager import DbManager
from seeder import DataSeeder
from session_manager import SessionManager

def main():
    app = QApplication(sys.argv)

    base_directory = Path(__file__).resolve().parent
    database = Database(database_url=f"sqlite:///{base_directory / 'cheatsheet.db'}")
    initialize_database(
        database=database,
        seeder=DataSeeder(json_path=base_directory / "initial_data.json")
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