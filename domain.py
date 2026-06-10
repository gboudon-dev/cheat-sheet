class User():
    def __init__(self, user_id: int, name: str, mail: str, notes: list["Note"] = None):
        self._user_id = user_id
        self._name = name
        self._mail = mail
        self._notes = notes if notes is not None else []
    
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
    def __init__(self, 
                 user_id: int, 
                 note_id: int | None = None,               
                 appearance: NoteConfig = None, 
                 pos_x: int = 0, 
                 pos_y: int = 0, 
                 commands: list[Command] = None):
        self._note_id = note_id 
        self._user_id = user_id
        self._appearance = appearance if appearance is not None else NoteConfig()
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._commands = commands if commands is not None else []
    
    @property
    def note_id(self):
        return self._note_id

    def load_default_pack(self, language_default_pack: list[Command]) -> None:
        self._commands = language_default_pack

    def add_command(self, cmd: Command) -> None:
        self._commands.append(cmd)

    def remove_command(self, cmd: Command) -> None:
        self._commands.remove(cmd)

    def to_json(self) -> dict:

        commands = []
        
        for cmd in self._commands:
            commands.append(cmd.command_id)        
        
        json_object = {
            "note_id": self._note_id,
            "user_id": self._user_id,
            "items": commands,
            "pos_x": self._pos_x,
            "pos_y": self._pos_y,
            "appearance": self._appearance.to_json()
        }

        return json_object

    def sort_items(self) -> None:
        def get_command_name(cmd: Command) -> str:
            return cmd.name
        self._commands.sort(key=get_command_name)

    def update_position(self, new_x: int, new_y: int) -> None:
        self._pos_x = new_x
        self._pos_y = new_y


class NoteConfig():
    def __init__(self, 
                 theme_color: str = "yellow", 
                 opacity: float = 1.0, 
                 is_always_on_top: bool = True):
        self._theme_color = theme_color
        self._opacity = opacity
        self._is_always_on_top = is_always_on_top
    
    def update_config(self, **kwargs) -> bool:
        update_counter = 0
        for key, value in kwargs.items():
            if key == "theme_color":
                self._theme_color = value
                update_counter += 1
            elif key == "opacity":
                self._opacity = value
                update_counter += 1
            elif key == "is_always_on_top":
                self._is_always_on_top = value
                update_counter += 1
        if update_counter > 0:
            return True
        else:
            return False

    def reset_defaults(self) -> None:
        self._theme_color =  "yellow"
        self._opacity = 1.0 
        self._is_always_on_top = True

    def to_json(self) -> dict:
        json_object = {
            "theme_color": self._theme_color,
            "opacity": self._opacity,
            "is_always_on_top": self._is_always_on_top
        }
        return json_object

class Command:
    def __init__(
        self, 
        command_id: int,
        language_id: int, 
        name: str, 
        description: str, 
        example: str | None, 
        is_default: bool, 
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
    
