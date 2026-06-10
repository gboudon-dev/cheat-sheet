from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


class DbManager:
    def __init__(self, db_path: str = "sqlite:///cheatsheet.db"):
        self._db_path = db_path
        self._engine = create_engine(self._db_path, connect_args={"check_same_thread": False}) 
        self._CustomSession = sessionmaker(self._engine)
        Base.metadata.create_all(self._engine)
