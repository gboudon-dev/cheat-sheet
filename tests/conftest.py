import pytest
from PySide6.QtWidgets import QApplication

from app_controller import AppController
from db_manager import DbManager
from session_manager import SessionManager


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def test_db():
    db_path = "sqlite:///:memory:"
    return DbManager(db_path=db_path)


@pytest.fixture
def test_session_manager(test_db):
    return SessionManager(db_manager=test_db)


@pytest.fixture
def test_app_controller(test_session_manager):
    return AppController(session_manager=test_session_manager)