from db_manager import DbManager
from domain import Command, Language, Note, User


class SessionManager:
    def __init__(
            self,
            #cloud_sync: CloudSyncManager,
            db_manager: DbManager 
            ):
        self._db_manager = db_manager
        self._current_user : User = self._db_manager.get_local_user()
        self._languages : list[Language] = self._db_manager.get_languages()
        #self._cloud_sync = cloud_sync

    def get_notes(self) -> list[Note]:
        return list(self._current_user.notes)

    def create_note(self) -> Note | None:
        if self._current_user.can_add_note():
            new_note = Note(user_id=self._current_user.user_id)
            generated_id = self._db_manager.insert_new_note(new_note)
            new_note.note_id = generated_id
            self._current_user.add_note(new_note)
            
            return new_note
        return None

    def remove_note(self, note_id: int) -> None:
        self._db_manager.delete_note(note_id)
        self._current_user.remove_note(note_id)

    def close_note(self, note: Note) -> None:
        if note.is_empty():
            self.remove_note(note_id=note.note_id)

    def move_note(self, note: Note, x: int, y: int) -> None:
        if note.update_position(x, y):
            self._db_manager.save_note_state(note)

    def resize_note(self, note: Note, width: int, height: int) -> None:
        if note.update_size(width, height):
            self._db_manager.save_note_state(note)

    def set_note_always_on_top(self, note: Note, value: bool) -> None:
        if note.config.update(is_always_on_top=value):
            self._db_manager.save_note_state(note)
    
    def set_note_language(self, note: Note, language_id: int) -> None:
        default_commands = self._db_manager.get_default_commands(language_id)
        note.change_language(language_id, default_commands)
        self._db_manager.save_note_state(note)

    def add_command_to_note(self, note: Note, command: Command) -> None:
        if not note.add_command(command):
            return
        self._db_manager.increment_command_counter(command)
        self._db_manager.save_note_state(note)

    def remove_command_from_note(self, note: Note, command: Command) -> None:
        if note.remove_command(command):
            self._db_manager.save_note_state(note)

    def get_languages(self) -> list[Language]:
        return list(self._languages)

    def search_commands(self, language_id: int, keyword: str) -> list[Command]:
        return self._db_manager.get_commands(language_id, keyword)
            