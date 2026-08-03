from db_manager import DbManager
from domain import Note, User, Command

class SessionManager:
    def __init__(
            self,
            #cloud_sync: CloudSyncManager,
            db_manager: DbManager 
            ):
        db_manager.get_local_user_data()
        self._db_manager = db_manager
        self._current_user : User = self._db_manager.get_local_user_data()
        #self._cloud_sync = cloud_sync
        


    @property
    def current_user(self) -> User:
        return self._current_user

    def create_note(self) -> Note:
        new_note = Note(user_id=self._current_user._user_id)
        generated_id = self._db_manager.insert_new_note(new_note)
        new_note.note_id = generated_id
        self._current_user.add_note(new_note)
        
        return new_note

    def load_default_pack_to_note(self, note: Note, lang_id: int) -> None:
        default_commands = self._db_manager.get_default_commands(lang_id)
        note.load_default_pack(default_commands)
        self._db_manager.save_note_state(note)

    def search_commands(self, lang_id: int, keyword: str) -> list[Command]:
        return self._db_manager.get_commands(lang_id, keyword)

    def add_command_to_note(self, note: Note, command: Command) -> None:
        note.add_command(command)
        note.sort_items()
        self._db_manager.update_command_counter(command)
        self._db_manager.save_note_state(note)

    def remove_command_from_note(self, note: Note, command: Command) -> None:
        note.remove_command(command)
        self._db_manager.save_note_state(note)

    def remove_note(self, note_id: int) -> None:
        self._db_manager.delete_note(note_id)
        self._current_user.remove_note(note_id)

    def save_note_position_and_config(self, note: Note) -> None:
        self._db_manager.save_note_state(note)