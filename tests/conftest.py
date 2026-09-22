from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from app_controller import AppController
from bootstrap import initialize_database
from database import Database
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
def test_database():
    return Database(database_url="sqlite:///:memory:")


@pytest.fixture
def test_session_factory(test_database):
    return test_database.session_factory


@pytest.fixture
def test_db(test_database, test_seeder):
    initialize_database(database=test_database, seeder=test_seeder)
    return DbManager(session_factory=test_database.session_factory)


@pytest.fixture
def test_session_manager(test_db):
    return SessionManager(db_manager=test_db)


@pytest.fixture
def test_app_controller(test_session_manager):
    return AppController(session_manager=test_session_manager)