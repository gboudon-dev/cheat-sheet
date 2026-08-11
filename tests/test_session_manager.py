import pytest
from db_manager import DbManager
from domain import Command, Note
from session_manager import SessionManager
from models import CommandORM, LanguageORM

@pytest.fixture
def test_db():
    manager = DbManager(db_path="sqlite:///:memory:")
    return manager

@pytest.fixture
def session_mgr(test_db):
    return SessionManager(db_manager=test_db)

def test_session_manager_def_user_initialization(session_mgr):
    user = session_mgr.current_user
    assert user is not None
    assert user.user_id == DbManager.DEFAULT_LOCAL_USER_ID

def test_create_note_flow(session_mgr):
    new_note = session_mgr.create_note()
    
    assert isinstance(new_note, Note)
    assert new_note.note_id is not None  
    assert new_note.user_id == session_mgr.current_user.user_id
    assert len(session_mgr.current_user._notes) == 1

def test_add_command_and_counter_increment(session_mgr, test_db):
    with test_db._CustomSession() as session:
        lang = LanguageORM(language_id=1, name="Git")
        cmd_orm = CommandORM(
            command_id=10,
            language_id=1,
            name="git status",
            description="Muestra el estado del árbol de trabajo",
            example=None,
            is_default=True,
            counter=0
        )
        session.add(lang)
        session.add(cmd_orm)
        session.commit()

    note = session_mgr.create_note()
    commands_found = session_mgr.search_commands(lang_id=1, keyword="git status")
    assert isinstance(commands_found, list)
    cmd_to_add = commands_found[0]

    session_mgr.add_command_to_note(note, cmd_to_add)

    assert len(note.commands) == 1
    assert note.commands[0].name == "git status"
    with test_db._CustomSession() as session:
        updated_cmd = session.query(CommandORM).filter_by(command_id=10).first()
        assert updated_cmd.counter == 1

def test_get_languages(session_mgr, test_db):
    with test_db._CustomSession() as session:
        session.add(LanguageORM(language_id=1, name="git"))
        session.commit()

    languages = session_mgr.get_languages()

    assert len(languages) == 1
    assert languages[0].name == "git"
