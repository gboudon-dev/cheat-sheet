import pytest
from sqlalchemy.exc import IntegrityError

from db_manager import DbManager
from domain import Note
from models import LanguageORM, NoteORM, UserORM


def test_foreign_key_prevents_orphan_notes(test_db):
    invalid_note = Note(user_id=99999)
    with pytest.raises(IntegrityError):
        test_db.insert_new_note(invalid_note)


def test_get_languages_returns_domain_objects(test_db):
    languages = test_db.get_languages()

    assert len(languages) >= 1
    assert any(lang.name == "Git" for lang in languages)


def test_note_lifecycle(test_db: DbManager):
    # Creation
    note = Note(
        user_id=0,
    )

    note_id = test_db.insert_new_note(note)
    note.note_id = note_id

    with test_db._CustomSession() as session:
        created_note = session.query(NoteORM).filter_by(note_id=note_id).first()

        assert created_note is not None

    # Update
    note.update_position(new_x=474, new_y=372)
    note.update_size(new_width=543, new_height=321)

    with test_db._CustomSession() as session:
        test_db.save_note_state(note)
        updated_note = session.query(NoteORM).filter_by(note_id=note_id).first()

        assert updated_note.pos_x == 474
        assert updated_note.pos_y == 372
        assert updated_note.width == 543
        assert updated_note.height == 321

    # Delete
    test_db.delete_note(note_id=note.note_id)

    with test_db._CustomSession() as session:
        deleted_note = session.query(NoteORM).filter_by(note_id=note_id).first()

        assert deleted_note is None


def test_save_note_state_raises_error_with_nonexistent_id(test_db: DbManager):
    note = Note(user_id=0, note_id=999)

    with pytest.raises(ValueError, match="Note with id 999 does not exist in the database."):
        test_db.save_note_state(note=note)


def test_ensure_local_user_is_idempotent(tmp_path, test_seeder):
    db_file = tmp_path / "test_idempotency.db"
    database_url = f"sqlite:///{db_file}"

    db1 = DbManager(database_url=database_url)
    db1.initialize(seeder=test_seeder)
    db2 = DbManager(database_url=database_url)
    db2.initialize(seeder=test_seeder)

    with db2._CustomSession() as session:
        users = session.query(UserORM).all()

        assert len(users) == 1
        assert users[0].user_id == 0
        assert users[0].name == "Guest"


def test_constructor_does_not_create_database(tmp_path):
    db_file = tmp_path / "test.db"

    DbManager(database_url=f"sqlite:///{db_file}")

    assert not db_file.exists()
