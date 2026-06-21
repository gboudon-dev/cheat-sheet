from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, UserORM, NoteORM, CommandORM, LanguageORM
from schemas import UserDTO, NoteDTO, NoteConfigDTO, CommandDTO, LanguageDTO
from domain import User, Command, Note, NoteConfig, Language


class DbManager:
    def __init__(self, db_path: str = "sqlite:///cheatsheet.db"):
        self._db_path = db_path
        self._engine = create_engine(self._db_path, connect_args={"check_same_thread": False}) 
        self._CustomSession = sessionmaker(self._engine)
        Base.metadata.create_all(self._engine)
        self._ensure_local_user()
    
    def _ensure_local_user(self) -> None:
        with self._CustomSession() as session:
            local_user = session.query(UserORM).filter_by(user_id=0).first()
            if local_user:
                return None
            else:
                local_user = UserORM(
                    user_id = 0,
                    name = "Guest",
                )
                session.add(local_user)
                session.commit()
                return None
    
    def get_local_user_data(self) -> User:
        with self._CustomSession() as session:
            local_user_data = session.query(UserORM).filter_by(user_id=0).first()
            user_dict = UserDTO.model_validate(local_user_data).model_dump()
        
        notes_list = []    
        for note in user_dict["notes"]:
            
            command_list = []
            for command in note["commands"]:
                command_as_domain_object = Command(
                    command_id=command["command_id"],
                    language_id=command["language_id"],
                    name=command["name"],
                    description=command["description"],
                    example=command["example"],
                    is_default=command["is_default"],
                    counter=command["counter"]    
                )
                command_list.append(command_as_domain_object)
                
            note_config_as_domain_object = NoteConfig(
            theme_color=note["note_config"]["theme_color"],
            opacity=note["note_config"]["opacity"],
            is_always_on_top=note["note_config"]["is_always_on_top"]
        )
            note_as_domain_object = Note(
                user_id = note["note_id"],
                appearance= note_config_as_domain_object,
                pos_x= note["pos_x"],
                pos_y= note["pos_y"],
                commands= command_list
            )
            notes_list.append(note_as_domain_object)
        local_user = User(
            user_id = user_dict["user_id"],
            name = user_dict["name"],
            mail = user_dict["mail"],
            notes = notes_list
            )
        return local_user

    #def insert_new_note(self, note: Note) -> int:
        #with self._CustomSession() as session:
            #session.query(NoteORM)
