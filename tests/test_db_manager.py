import pytest
from sqlalchemy.exc import IntegrityError
from db_manager import DbManager
from domain import Note

@pytest.fixture
def db():
    return DbManager(db_path="sqlite:///:memory:")

def test_foreign_key_prevents_orphan_notes(db):
    invalid_note = Note(user_id=99999)
    with pytest.raises(IntegrityError):
        db.insert_new_note(invalid_note)