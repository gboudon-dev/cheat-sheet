import pytest
from cheatsheet.domain.models import User

@pytest.mark.usefixtures("qapp")
def test_open_note_window_registers_window(test_session_manager, test_app_controller):
    assert len(test_app_controller._windows) == 0

    note = test_session_manager.create_note()
    window = test_app_controller.open_note_window(note)

    assert len(test_app_controller._windows) == 1
    assert test_app_controller._windows[note.note_id] is window

    window.close()

@pytest.mark.usefixtures("qapp")
def test_new_note_requested_signal_opens_new_window(test_session_manager, test_app_controller):
    initial_note = test_session_manager.create_note()
    initial_window = test_app_controller.open_note_window(initial_note)

    assert len(test_app_controller._windows) == 1

    initial_window.new_note_requested.emit(initial_note)

    assert len(test_app_controller._windows) == 2
    
