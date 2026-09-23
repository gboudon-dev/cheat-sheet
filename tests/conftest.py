from importlib.resources import files

import pytest
from PySide6.QtWidgets import QApplication

from cheatsheet.presentation.app_controller import AppController
from cheatsheet.infrastructure.bootstrap import initialize_database
from cheatsheet.infrastructure.database import Database
from cheatsheet.infrastructure.db_manager import DbManager
from cheatsheet.infrastructure.seeder import DataSeeder
from cheatsheet.application.session_manager import SessionManager


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def test_seeder():
    json_path = files("cheatsheet.infrastructure") / "initial_data.json"
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