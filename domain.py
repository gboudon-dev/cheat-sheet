from __future__ import annotations

class User():
    MAX_NOTES: int = 5

    def __init__(self, user_id: int, name: str, mail: str, notes: list["Note"] | None = None):
        self._user_id = user_id
        self._name = name
        self._mail = mail
        self._notes = notes if notes is not None else []

    @property
    def user_id(self):
        return self._user_id

    @property
    def notes(self):
        return self._notes
    
    def load_user(self, data: dict) -> None:
        self._user_id = data["user_id"]
        self._name = data["name"]
        self._mail = data["mail"]
        self._notes = data["notes"] if data["notes"] is not None else []
        
    def is_active(self) -> bool:
        pass

    def can_add_note(self) -> bool:
        return len(self._notes) < self.MAX_NOTES
     
    def add_note(self, note : Note) -> bool:
        if self.can_add_note():
            self._notes.append(note)
            return True
        return False
        
    def remove_note(self, note_id: int) -> None:
        for note in self._notes:
            if note_id == note.note_id:
                self._notes.remove(note)
    
    def logout(self) -> None:
        pass

class Note():
    MIN_WIDTH: int = 220
    MIN_HEIGHT: int = 150

    def __init__(self,
                 user_id: int,
                 note_id: int | None = None,
                 config: NoteConfig = None,
                 pos_x: int = 0,
                 pos_y: int = 0,
                 width: int = 400,
                 height: int = 220,
                 language_id: int | None = None,
                 commands: list[Command] | None = None):
        self._note_id = note_id
        self._user_id = user_id
        self._config = config if config is not None else NoteConfig()
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._width = max(width, self.MIN_WIDTH)
        self._height = max(height, self.MIN_HEIGHT)
        self._language_id = language_id
        self._commands = commands if commands is not None else []
        self._sort_commands()

    @property 
    def user_id(self) -> int:
        return self._user_id
        
    @property
    def note_id(self) -> int:
        return self._note_id

    @note_id.setter
    def note_id(self, value):
        self._note_id = value

    @property
    def language_id(self) -> int | None:
        return self._language_id

    @property
    def pos_x(self) -> int:
        return self._pos_x

    @property
    def pos_y(self) -> int:
        return self._pos_y

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def config(self):
        return self._config

    @property
    def commands(self) -> list:
        return self._commands

    def change_language(self, language_id: int, default_commands: list[Command]) -> None:
        self._language_id = language_id
        self._commands = default_commands
        self._sort_commands()

    def add_command(self, cmd: Command) -> bool:
        for existing_cmd in self._commands:
            if existing_cmd.command_id == cmd.command_id:
                return False
        self._commands.append(cmd)
        self._sort_commands()
        return True

    def remove_command(self, cmd: Command) -> bool:
        for existing_cmd in self._commands:
            if existing_cmd.command_id == cmd.command_id:
                self._commands.remove(existing_cmd)
                return True
        return False

    def is_empty(self) -> bool:
        return len(self._commands) == 0

    def _sort_commands(self) -> None:
        def get_command_name(cmd: Command) -> str:
            return cmd.name
        self._commands.sort(key=get_command_name)

    def update_size(self, new_width: int, new_height: int) -> bool:
        width = max(new_width, self.MIN_WIDTH)
        height = max(new_height, self.MIN_HEIGHT)
        if width == self._width and height == self._height:
            return False
        self._width = width
        self._height = height
        return True

    def update_position(self, new_x: int, new_y: int) -> bool:
        if new_x == self._pos_x and new_y == self._pos_y:
            return False
        self._pos_x = new_x
        self._pos_y = new_y
        return True

class NoteConfig():
    DEFAULT_THEME: str = "modern"
    DEFAULT_IS_ALWAYS_ON_TOP: bool = True

    def __init__(self, 
                 theme: str = DEFAULT_THEME, 
                 is_always_on_top: bool = DEFAULT_IS_ALWAYS_ON_TOP):
        self._theme = theme
        self._is_always_on_top = is_always_on_top

    @property
    def theme(self):
        return self._theme

    @property
    def is_always_on_top(self):
        return self._is_always_on_top
    
    def update(self, **kwargs) -> bool:
        update_counter = 0
        for key, value in kwargs.items():
            if key == "theme":
                if self._theme != value:
                    self._theme = value
                    update_counter += 1
            elif key == "is_always_on_top":
                if self._is_always_on_top != value:
                    self._is_always_on_top = value
                    update_counter += 1
            else:
                raise ValueError(f"Unknown configuration key: {key}")
        return update_counter > 0


class Example:
    def __init__(self, code: str, comment: str | None = None):
        self._code = code
        self._comment = comment

    @property
    def code(self) -> str:
        return self._code

    @property
    def comment(self) -> str | None:
        return self._comment

class Command:
    def __init__(
        self, 
        command_id: int,
        language_id: int, 
        name: str, 
        description: str, 
        is_default: bool,
        examples: list[Example] | None = None,
        counter: int = 0
    ):
        self._command_id = command_id
        self._language_id = language_id
        self._name = name
        self._description = description
        self._examples = examples
        self._is_default = is_default
        self._counter = counter

    @property
    def command_id(self) -> int:
        return self._command_id
    
    @property
    def language_id(self) -> int:
        return self._language_id
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def examples(self) -> list[Example] | None:
        return self._examples

class Language:
    def __init__(self, language_id: int, name: str):
        self._language_id = language_id
        self._name = name
    
    @property
    def language_id(self) -> int:
        return self._language_id

    @property
    def name(self) -> str:
        return self._name
    
