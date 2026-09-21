from sqlalchemy import create_engine, event, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from models import Base, UserORM, NoteORM, CommandORM, LanguageORM
from domain import User, Command, Example, Note, NoteConfig, Language
from seeder import DataSeeder

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class DbManager:
    DEFAULT_LOCAL_USER_ID: int = 0

    def __init__(self, db_path: str = "sqlite:///cheatsheet.db"):
        self._db_path = db_path
        self._engine = create_engine(self._db_path, connect_args={"check_same_thread": False}) 
        self._CustomSession = sessionmaker(self._engine)
        Base.metadata.create_all(self._engine)
        self._ensure_local_user()
        self._ensure_initial_data()
    
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

    def _ensure_initial_data(self) -> None:
        with self._CustomSession() as session:
            seeder = DataSeeder()
            seeder.seed_initial_languages(session=session)
    
    def _to_domain_command(self, command_orm: CommandORM) -> Command:
        examples = None
        if command_orm.examples is not None:
            examples = []
            for example_data in command_orm.examples:
                examples.append(Example(code=example_data["code"], comment=example_data.get("comment")))

        command = Command(
            command_id=command_orm.command_id,
            language_id=command_orm.language_id,
            name=command_orm.name,
            description=command_orm.description,
            examples=examples,
            is_default=command_orm.is_default,
            counter=command_orm.counter
        )
        return command

    def get_local_user(self, user_id: int = DEFAULT_LOCAL_USER_ID) -> User:
        with self._CustomSession() as session:
            local_user_data = session.query(UserORM).filter_by(user_id=user_id).first()

            if not local_user_data:
                raise ValueError(f"User with id {user_id} does not exist in the database.")
          
            notes_list = []  
              
            for note_orm in local_user_data.notes:
                
                command_list = []

                for command_orm in note_orm.commands:
                    command_list.append(self._to_domain_command(command_orm))

                note_config_as_domain_object = NoteConfig(
                theme_color=note_orm.note_config["theme_color"],
                opacity=note_orm.note_config["opacity"],
                is_always_on_top=note_orm.note_config["is_always_on_top"]
            )
                note_as_domain_object = Note(
                    user_id = user_id,
                    note_id = note_orm.note_id,
                    language_id = note_orm.language_id,
                    config= note_config_as_domain_object,
                    pos_x= note_orm.pos_x,
                    pos_y= note_orm.pos_y,
                    width= note_orm.width,
                    height= note_orm.height,
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
                width = note.width,
                height = note.height,
                language_id = note.language_id,
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
                raise ValueError(f"Note with id {note.note_id} does not exist in the database.")
            
            current_note_orm.pos_x = note.pos_x
            current_note_orm.pos_y = note.pos_y
            current_note_orm.width = note.width
            current_note_orm.height = note.height
            current_note_orm.language_id = note.language_id
            current_note_orm.note_config = note.config.to_dict()

            command_ids = [command.command_id for command in note.commands] 
            current_note_orm.commands = session.query(CommandORM).filter(CommandORM.command_id.in_(command_ids)).all()
            session.commit()

    def delete_note(self, note_id: int) -> None:
        with self._CustomSession() as session:
            note_to_delete = session.query(NoteORM).filter_by(note_id=note_id).first()
            if note_to_delete:
                session.delete(note_to_delete)
                session.commit()

    def get_default_commands(self, language_id: int) -> list[Command]:
        with self._CustomSession() as session:
            default_commands_orm = session.query(CommandORM).filter_by(language_id=language_id, is_default=True).all()
            domain_commands = []
            for command_orm in default_commands_orm:
                domain_commands.append(self._to_domain_command(command_orm))
            return domain_commands

    def get_commands(self, language_id: int, keyword: str) -> list[Command]:
        with self._CustomSession() as session:
            commands_orm = (
                session.query(CommandORM).filter(
                CommandORM.language_id == language_id,
                CommandORM.name.ilike(f"%{keyword}%")
                ).all()
            )

            domain_commands = []

            for command_orm in commands_orm:
                domain_commands.append(self._to_domain_command(command_orm))

            return domain_commands

    def get_languages(self) -> list[Language]:
        with self._CustomSession() as session:
            languages_orm = session.query(LanguageORM).order_by(func.lower(LanguageORM.name)).all()
            domain_languages = []
            for language_orm in languages_orm:
                language = Language(
                    language_id=language_orm.language_id,
                    name=language_orm.name
                )
                domain_languages.append(language)
            return domain_languages

    def sync_commands(self, data: dict) -> bool:
        pass

    def increment_command_counter(self, command: Command) -> None:
        with self._CustomSession() as session:
            current_command_orm = session.query(CommandORM).filter_by(command_id=command.command_id).first()
            if current_command_orm:
                current_command_orm.counter += 1
                session.commit()

    def update_schema(self, to_version: str) -> bool:
        pass
        
