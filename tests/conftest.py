from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from app_controller import AppController
from db_manager import DbManager
from seeder import DataSeeder
from session_manager import SessionManager


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def test_seeder():
    json_path = Path(__file__).resolve().parent.parent / "initial_data.json"
    return DataSeeder(json_path=json_path)


@pytest.fixture
def test_db(test_seeder):
    database_url = "sqlite:///:memory:"
    db_manager = DbManager(database_url=database_url)
    db_manager.initialize(seeder=test_seeder)
    return db_manager


@pytest.fixture
def test_session_manager(test_db):
    return SessionManager(db_manager=test_db)


@pytest.fixture
def test_app_controller(test_session_manager):
    return AppController(session_manager=test_session_manager)