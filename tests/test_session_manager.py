import pytest
from db_manager import DbManager
from domain import Command, Note, User
from session_manager import SessionManager
from models import CommandORM, LanguageORM

@pytest.fixture
def test_db():
    manager = DbManager(db_path="sqlite:///:memory:")
    return manager

@pytest.fixture
def seeded_db(test_db):
    with test_db._CustomSession() as session:
        language = LanguageORM(language_id=1, name="Git")
        command_orm = CommandORM(
            command_id=10,
            language_id=1,
            name="git status",
            description="Show the working tree status",
            example=None,
            is_default=True,
            counter=0
        )
        session.add(language)
        session.add(command_orm)
        session.commit()
    return test_db

@pytest.fixture
def session_manager(test_db):
    return SessionManager(db_manager=test_db)

def test_add_command_and_counter_increment(session_manager, seeded_db):
    note = session_manager.create_note()
    commands_found = session_manager.search_commands(language_id=1, keyword="git status")
    assert isinstance(commands_found, list)
    command_to_add = commands_found[0]

    session_manager.add_command_to_note(note, command_to_add)

    assert len(note.commands) == 1
    assert note.commands[0].name == "git status"
    with seeded_db._CustomSession() as session:
        updated_cmd = session.query(CommandORM).filter_by(command_id=10).first()
        assert updated_cmd.counter == 1

def test_get_languages(test_db):
    with test_db._CustomSession() as session:
        session.add(LanguageORM(language_id=1, name="git"))
        session.commit()

    session_manager = SessionManager(db_manager=test_db)
    languages = session_manager.get_languages()

    assert len(languages) == 1
    assert languages[0].name == "git"

def test_create_note_returns_none_when_capped(session_manager):
    for _ in range(User.MAX_NOTES):
        assert session_manager.create_note() is not None

    extra_note = session_manager.create_note()

    assert extra_note is None
    assert len(session_manager.get_notes()) == User.MAX_NOTES

def test_add_duplicate_command_is_ignored(session_manager, seeded_db):
    note = session_manager.create_note()
    assert len(note.commands) == 0

    command = Command(
        command_id=10,
        language_id=1,
        name="git status",
        description="Show the working tree status",
        is_default=True,
    )
    # adding the same command twice must not duplicate it
    session_manager.add_command_to_note(note=note, command=command)
    session_manager.add_command_to_note(note=note, command=command)

    assert len(note.commands) == 1

    with seeded_db._CustomSession() as session:
        stored_command = session.query(CommandORM).filter_by(command_id=10).first()
        assert stored_command.counter == 1


