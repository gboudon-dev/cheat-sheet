import sys

from PySide6.QtWidgets import QApplication

from app_controller import AppController
from db_manager import DbManager
from session_manager import SessionManager

GIT_LANGUAGE_ID = 1


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    db_mgr = DbManager()
    session_mgr = SessionManager(db_manager=db_mgr)
    controller = AppController(session_manager=session_mgr)

    note = session_mgr.create_note()
    session_mgr.load_default_pack_to_note(note, GIT_LANGUAGE_ID)
    controller.open_note_window(note)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()