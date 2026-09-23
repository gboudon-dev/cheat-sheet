from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from cheatsheet.infrastructure.orm import Base

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class Database:
    def __init__(self, database_url: str):
        self._database_url = database_url
        self._engine = create_engine(self._database_url, connect_args={"check_same_thread": False})
        self._session_factory = sessionmaker(self._engine)

    @property
    def session_factory(self) -> sessionmaker:
        return self._session_factory

    def create_schema(self) -> None:
        Base.metadata.create_all(self._engine, checkfirst=True)
