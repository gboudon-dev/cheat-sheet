from domain import NoteConfig, Note, Command
import pytest

def test_update_values_flow():
    config = NoteConfig()

    assert config.theme == NoteConfig.DEFAULT_THEME
    assert config.is_always_on_top is True

    update_items = {
        "theme": "classic",
        "is_always_on_top": False
    }
    response_status = config.update(**update_items)

    assert response_status is True
    assert config.theme == "classic"
    assert config._is_always_on_top is False

def test_sort_commands():
    note = Note(user_id=0)
    cmd1 = Command(command_id=1, language_id=0, name="Zelia",description="", is_default=True)
    cmd2 = Command(command_id=2, language_id=0, name="Avatar",description="", is_default=True)
    note.add_command(cmd1)
    note.add_command(cmd2)

    assert note.commands[0].name == "Avatar"
    assert note.commands[1].name == "Zelia" 

def test_update_position_returns_true_when_successful():
    note = Note(user_id=0)
    
    assert note.pos_x == 0
    assert note.pos_y == 0
    
    update = note.update_position(new_x=100, new_y=2000)
    
    assert update is True
    assert note.pos_x == 100
    assert note.pos_y == 2000
    
def test_update_position_returns_false_when_unchanged():
    note = Note(user_id=0)
    update = note.update_position(new_x=0, new_y=0)
    
    assert update is False

@pytest.mark.parametrize("new_width, new_height", [
    (Note.MIN_WIDTH - 50, Note.MIN_HEIGHT - 30),
    (Note.MIN_WIDTH - 1, Note.MIN_HEIGHT - 1),
])
def test_update_size_respects_min_values(new_width, new_height):
    note = Note(user_id=0, width=400, height=220)

    update = note.update_size(
        new_height=new_height, 
        new_width=new_width)

    assert update is True
    assert note.height == note.MIN_HEIGHT
    assert note.width == note.MIN_WIDTH
