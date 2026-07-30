from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, UserORM, NoteORM, CommandORM, LanguageORM
from schemas import UserDTO, NoteDTO, NoteConfigDTO, CommandDTO, LanguageDTO
from domain import User, Command, Note, NoteConfig, Language


class DbManager:
    DEFAULT_LOCAL_USER_ID: int = 0

    def __init__(self, db_path: str = "sqlite:///cheatsheet.db"):
        self._db_path = db_path
        self._engine = create_engine(self._db_path, connect_args={"check_same_thread": False}) 
        self._CustomSession = sessionmaker(self._engine)
        Base.metadata.create_all(self._engine)
        self._ensure_local_user()
    
    def _ensure_local_user(self) -> None:
        with self._CustomSession() as session:
            local_user = session.query(UserORM).filter_by(user_id=self.DEFAULT_LOCAL_USER_ID).first()
            if local_user:
                return None
            else:
                local_user = UserORM(
                    user_id = self.DEFAULT_LOCAL_USER_ID,
                    name = "Guest",
                )
                session.add(local_user)
                session.commit()
                return None
    
    def get_local_user_data(self, user_id: int) -> User:
        with self._CustomSession() as session:
            local_user_data = session.query(UserORM).filter_by(user_id=user_id).first()

            if not local_user_data:
                raise ValueError(f"User with id: {user_id} doesn't exist in database.")
          
        
            notes_list = []  
              
            for note_orm in local_user_data.notes:
                
                command_list = []

                for command in note_orm.commands:
                    command_as_domain_object = Command(
                        command_id=command.command_id,
                        language_id=command.language_id,
                        name=command.name,
                        description=command.description,
                        example=command.example,
                        is_default=command.is_default,
                        counter=command.counter    
                    )

                    command_list.append(command_as_domain_object)
                    
                note_config_as_domain_object = NoteConfig(
                theme_color=note_orm.note_config["theme_color"],
                opacity=note_orm.note_config["opacity"],
                is_always_on_top=note_orm.note_config["is_always_on_top"]
            )
                note_as_domain_object = Note(
                    user_id = user_id,
                    note_id = note_orm.note_id,
                    config= note_config_as_domain_object,
                    pos_x= note_orm.pos_x,
                    pos_y= note_orm.pos_y,
                    commands= command_list
                )
                notes_list.append(note_as_domain_object)
            local_user = User(
                user_id = local_user_data.user_id,
                name = local_user_data.name,
                mail = local_user_data.mail,
                notes = notes_list
                )
            return local_user

    def insert_new_note(self, note: Note) -> int:
        with self._CustomSession() as session:
            new_note = NoteORM(
                user_id = note.user_id,
                pos_x = note.pos_x,
                pos_y = note.pos_y,
                note_config= note.config.to_dict(), 
            )

            session.add(new_note)
            session.commit()
            session.refresh(new_note)
            return new_note.note_id
            
    def save_note_state(self, note: Note) -> None:
        with self._CustomSession() as session:
            current_note_orm = session.query(NoteORM).filter_by(note_id=note.note_id).first()

            if not current_note_orm:
                raise ValueError(f"Note with id {note.note_id} does not exist in database.")
            
            current_note_orm.pos_x = note.pos_x
            current_note_orm.pos_y = note.pos_y
            current_note_orm.note_config = note.config.to_dict()

            cmd_ids = [cmd.command_id for cmd in note.commands] 
            current_note_orm.commands = session.query(CommandORM).filter(CommandORM.command_id.in_(cmd_ids)).all()
            session.commit()

    def delete_note(self, note_id: int) -> None:
        with self._CustomSession() as session:
            note_to_delete = session.query(NoteORM).filter_by(note_id=note_id).first()
            if note_to_delete:
                session.delete(note_to_delete)
                session.commit()

    def get_default_commands(self, lang_id: int) -> list[Command]:
        with self._CustomSession() as session:
            default_commands_orm = session.query(CommandORM).filter_by(language_id=lang_id, is_default=True).all()
            domain_commands = []
            for cmd_orm in default_commands_orm:
                cmd_obj = Command(
                    command_id=cmd_orm.command_id,
                    language_id=cmd_orm.language_id,
                    name=cmd_orm.name,
                    description=cmd_orm.description,
                    example=cmd_orm.example,
                    is_default=cmd_orm.is_default,
                    counter=cmd_orm.counter
                )
                domain_commands.append(cmd_obj)
            return domain_commands

    def get_commands(self, lang_id: int, keyword: str) -> list[Command]:
        with self._CustomSession() as session:
            commands_orm = (
                session.query(CommandORM).filter(
                CommandORM.language_id == lang_id,
                CommandORM.name.ilike(f"%{keyword}%")
                ).all()
            )

            domain_commands = []

            for cmd_orm in commands_orm:
                cmd_obj = Command(
                    command_id=cmd_orm.command_id,
                    language_id=cmd_orm.language_id,
                    name=cmd_orm.name,
                    description=cmd_orm.description,
                    example=cmd_orm.example,
                    is_default=cmd_orm.is_default,
                    counter=cmd_orm.counter
                )
                domain_commands.append(cmd_obj)

            return domain_commands

    def sync_commands(self, data: dict) -> bool:
        pass

    def update_command_counter(self, cmd: Command) -> None:
        pass

    def update_schema(self, to_version: str) -> bool:
        pass
        
