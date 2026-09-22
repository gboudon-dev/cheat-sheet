import pytest
from db_manager import DbManager
from domain import Command, Note, User
from session_manager import SessionManager
from models import CommandORM, LanguageORM


@pytest.fixture
def seeded_db(test_db, test_session_factory):
    with test_session_factory() as session:
        git_lang = session.query(LanguageORM).filter_by(name="Git").first()
        if not git_lang:
            git_lang = LanguageORM(language_id=1, name="Git")
            session.add(git_lang)
            session.commit()

        status_cmd = session.query(CommandORM).filter_by(name="git status").first()
        if not status_cmd:
            status_cmd = CommandORM(
                command_id=10,
                language_id=git_lang.language_id,
                name="git status",
                description="Show the working tree status",
                examples=None,
                is_default=True,
                counter=0
            )
            session.add(status_cmd)
            session.commit()
    return test_db


def test_add_command_and_counter_increment(test_session_manager, seeded_db, test_session_factory):
    note = test_session_manager.create_note()
    commands_found = test_session_manager.search_commands(language_id=1, keyword="git status")
    assert isinstance(commands_found, list)
    command_to_add = commands_found[0]

    test_session_manager.add_command_to_note(note, command_to_add)

    assert len(note.commands) == 1
    assert note.commands[0].name == "git status"
    with test_session_factory() as session:
        updated_cmd = session.query(CommandORM).filter_by(command_id=command_to_add.command_id).first()
        assert updated_cmd.counter == 1


def test_get_languages(test_db):
    sm = SessionManager(db_manager=test_db)
    languages = sm.get_languages()

    assert len(languages) >= 1
    assert any(lang.name == "Git" for lang in languages)


def test_create_note_returns_none_when_capped(test_session_manager):
    for _ in range(User.MAX_NOTES):
        assert test_session_manager.create_note() is not None

    extra_note = test_session_manager.create_note()

    assert extra_note is None
    assert len(test_session_manager.get_notes()) == User.MAX_NOTES


def test_add_duplicate_command_is_ignored(test_session_manager, seeded_db, test_session_factory):
    note = test_session_manager.create_note()
    assert len(note.commands) == 0

    command = Command(
        command_id=10,
        language_id=1,
        name="git status",
        description="Show the working tree status",
        is_default=True,
    )
    # adding the same command twice must not duplicate it
    test_session_manager.add_command_to_note(note=note, command=command)
    test_session_manager.add_command_to_note(note=note, command=command)

    assert len(note.commands) == 1

    with test_session_factory() as session:
        stored_command = session.query(CommandORM).filter_by(command_id=10).first()
        assert stored_command.counter == 1
