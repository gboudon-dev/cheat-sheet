import sys

from PySide6.QtWidgets import QApplication

from app_controller import AppController
from db_manager import DbManager
from session_manager import SessionManager

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    db_mgr = DbManager()
    session_manager = SessionManager(db_manager=db_mgr)
    app_controller = AppController(session_manager=session_manager)

    if not app_controller.open_saved_notes():
        note = session_manager.create_note()
        app_controller.open_note_window(note)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()