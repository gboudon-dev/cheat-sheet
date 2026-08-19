from __future__ import annotations

class User():
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

    def add_note(self, note : Note) -> None:
        self._notes.append(note)
        
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
                 commands: list[Command] | None = None):
        self._note_id = note_id
        self._user_id = user_id
        self._config = config if config is not None else NoteConfig()
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._width = max(width, self.MIN_WIDTH)
        self._height = max(height, self.MIN_HEIGHT)
        self._commands = commands if commands is not None else []

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

    def load_default_pack(self, language_default_pack: list[Command]) -> None:
        self._commands = language_default_pack

    def add_command(self, cmd: Command) -> bool:
        for existing_cmd in self._commands:
            if existing_cmd.command_id == cmd.command_id:
                return False
        self._commands.append(cmd)
        self.sort_items()
        return True

    def remove_command(self, cmd: Command) -> bool:
        for existing_cmd in self._commands:
            if existing_cmd.command_id == cmd.command_id:
                self._commands.remove(existing_cmd)
                return True
        return False

    def to_dict(self) -> dict:

        commands = []
        
        for cmd in self._commands:
            commands.append(cmd.command_id)        
        
        cmds_as_dict = {
            "note_id": self._note_id,
            "user_id": self._user_id,
            "items": commands,
            "pos_x": self._pos_x,
            "pos_y": self._pos_y,
            "width": self._width,
            "height": self._height,
            "config": self._config.to_dict()
        }

        return cmds_as_dict

    def sort_items(self) -> None:
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
    def __init__(self, 
                 theme_color: str = "yellow", 
                 opacity: float = 1.0, 
                 is_always_on_top: bool = True):
        self._theme_color = theme_color
        self._opacity = opacity
        self._is_always_on_top = is_always_on_top

    @property
    def theme_color(self):
        return self._theme_color

    @property
    def opacity(self):
        return self._opacity

    @property
    def is_always_on_top(self):
        return self._is_always_on_top
    
    def update_config(self, **kwargs) -> bool:
        update_counter = 0
        for key, value in kwargs.items():
            if key == "theme_color":
                if self._theme_color != value:
                    self._theme_color = value
                    update_counter += 1
            elif key == "opacity":
                if self._opacity != value:
                    self._opacity = value
                    update_counter += 1
            elif key == "is_always_on_top":
                if self._is_always_on_top != value:
                    self._is_always_on_top = value
                    update_counter += 1
            else:
                raise ValueError(f"Unknown configuration key: {key}")
        return update_counter > 0

    def reset_defaults(self) -> None:
        self._theme_color =  "yellow"
        self._opacity = 1.0 
        self._is_always_on_top = True

    def to_dict(self) -> dict:
        config_as_dict = {
            "theme_color": self._theme_color,
            "opacity": self._opacity,
            "is_always_on_top": self._is_always_on_top
        }
        return config_as_dict

class Command:
    def __init__(
        self, 
        command_id: int,
        language_id: int, 
        name: str, 
        description: str, 
        is_default: bool,
        example: str | None = None, 
        counter: int = 0
    ):
        self._command_id = command_id
        self._language_id = language_id
        self._name = name
        self._description = description
        self._example = example
        self._is_default = is_default
        self._counter = counter

    @property
    def command_id(self) -> int:
        return self._command_id
    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def example(self) -> str | None:
        return self._example

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
    
