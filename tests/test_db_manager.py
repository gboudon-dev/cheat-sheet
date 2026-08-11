import pytest
from sqlalchemy.exc import IntegrityError

from db_manager import DbManager
from domain import Note
from models import LanguageORM


@pytest.fixture
def db():
    return DbManager(db_path="sqlite:///:memory:")

def test_foreign_key_prevents_orphan_notes(db):
    invalid_note = Note(user_id=99999)
    with pytest.raises(IntegrityError):
        db.insert_new_note(invalid_note)

def test_get_languages_returns_domain_objects(db):
    with db._CustomSession() as session:
        session.add_all([
            LanguageORM(language_id=1, name="git"),
            LanguageORM(language_id=2, name="python"),
        ])
        session.commit()

    languages = db.get_languages()

    assert {lang.name for lang in languages} == {"git", "python"}