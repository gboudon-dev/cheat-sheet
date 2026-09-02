from domain import NoteConfig, Note, Command

def test_update_config_values_flow():
    config = NoteConfig()

    assert config.theme_color == "yellow"
    assert config.opacity == 1.0
    assert config.is_always_on_top is True

    update_items = {
        "theme_color": "blue",
        "opacity": 0.5,
        "is_always_on_top": False
    }
    response_status = config.update_config(**update_items)

    assert response_status is True
    assert config.theme_color == "blue"
    assert config.opacity == 0.5
    assert config._is_always_on_top is False

def test_sort_items():
    note = Note(user_id=0)
    cmd1 = Command(command_id=1, language_id=0, name="Zelia",description="", is_default=True)
    cmd2 = Command(command_id=2, language_id=0, name="Avatar",description="", is_default=True)
    note.add_command(cmd1)
    note.add_command(cmd2)
    note.sort_items()

    assert note.commands[0].name == "Avatar"
    assert note.commands[1].name == "Zelia" 

def test_update_position_return_true_when_successful():
    note = Note(user_id=0)
    
    assert note.pos_x == 0
    assert note.pos_y == 0
    
    update = note.update_position(new_x=100, new_y=2000)
    
    assert update is True
    assert note.pos_x == 100
    assert note.pos_y == 2000
    
def test_update_position_return_false_when_unchanged():
    note = Note(user_id=0)
    update = note.update_position(new_x=0, new_y=0)
    
    assert update is False
      
def test_update_size_respect_min_values():
    note = Note(user_id=0)
    update = note.update_size(new_height=149, new_width=219)
    
    assert update is False
     