import pytest
from sqlalchemy.exc import IntegrityError

from cheatsheet.infrastructure.bootstrap import initialize_database
from cheatsheet.infrastructure.database import Database
from cheatsheet.infrastructure.db_manager import DbManager
from cheatsheet.domain.models import Example, Note
from cheatsheet.infrastructure.orm import CommandORM, LanguageORM, NoteORM, UserORM


def test_foreign_key_prevents_orphan_notes(test_db):
    invalid_note = Note(user_id=99999)
    with pytest.raises(IntegrityError):
        test_db.insert_new_note(invalid_note)


def test_get_languages_returns_domain_objects(test_db):
    languages = test_db.get_languages()

    assert len(languages) >= 1
    assert any(lang.name == "Git" for lang in languages)


def test_note_lifecycle(test_db: DbManager, test_session_factory):
    # Creation
    note = Note(
        user_id=0,
    )

    note_id = test_db.insert_new_note(note)
    note.note_id = note_id

    with test_session_factory() as session:
        created_note = session.query(NoteORM).filter_by(note_id=note_id).first()

        assert created_note is not None

    # Update
    note.update_position(new_x=474, new_y=372)
    note.update_size(new_width=543, new_height=321)

    with test_session_factory() as session:
        test_db.save_note_state(note)
        updated_note = session.query(NoteORM).filter_by(note_id=note_id).first()

        assert updated_note.pos_x == 474
        assert updated_note.pos_y == 372
        assert updated_note.width == 543
        assert updated_note.height == 321

    # Delete
    test_db.delete_note(note_id=note.note_id)

    with test_session_factory() as session:
        deleted_note = session.query(NoteORM).filter_by(note_id=note_id).first()

        assert deleted_note is None


def test_save_note_state_raises_error_with_nonexistent_id(test_db: DbManager):
    note = Note(user_id=0, note_id=999)

    with pytest.raises(ValueError, match="Note with id 999 does not exist in the database."):
        test_db.save_note_state(note=note)


def test_seed_local_user_is_idempotent(tmp_path, test_seeder):
    db_file = tmp_path / "test_idempotency.db"
    database_url = f"sqlite:///{db_file}"

    database1 = Database(database_url=database_url)
    initialize_database(database=database1, seeder=test_seeder)

    database2 = Database(database_url=database_url)
    initialize_database(database=database2, seeder=test_seeder)

    with database2.session_factory() as session:
        users = session.query(UserORM).all()

        assert len(users) == 1
        assert users[0].user_id == 0
        assert users[0].name == "Guest"


def test_constructor_does_not_create_database(tmp_path):
    db_file = tmp_path / "test.db"

    Database(database_url=f"sqlite:///{db_file}")

    assert not db_file.exists()


def test_command_examples_are_mapped_to_domain_objects(test_db, test_session_factory):
    with test_session_factory() as session:
        language = LanguageORM(name="Test language")
        command = CommandORM(
            language=language,
            name="git status",
            description="Show the working tree status",
            examples=[
                {"code": "git status -s", "comment": "Short format"},
                {"code": "git status"}
            ],
            is_default=True
        )
        session.add(command)
        session.commit()
        language_id = language.language_id

    commands = test_db.get_default_commands(language_id)
    examples = commands[0].examples

    assert len(examples) == 2
    assert isinstance(examples[0], Example)
    assert examples[0].code == "git status -s"
    assert examples[0].comment == "Short format"
    assert examples[1].code == "git status"
    assert examples[1].comment is None
