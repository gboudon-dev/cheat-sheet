from domain import Command, Note
from session_manager import SessionManager
from ui.sticky_note import StickyNoteWindow


class AppController:
    def __init__(self, session_manager: SessionManager, on_all_windows_closed=None):
        self._session_manager = session_manager
        self._windows: dict[int, StickyNoteWindow] = {}
        self._languages = self._session_manager.get_languages()
        self._on_all_windows_closed=on_all_windows_closed

    def open_note_window(self, note: Note) -> StickyNoteWindow:
        window = StickyNoteWindow(note=note, languages=self._languages)
        window.always_on_top_changed.connect(self._on_always_on_top_changed)
        window.new_note_requested.connect(self._on_new_note_requested)
        window.delete_requested.connect(self._on_delete_requested)
        window.login_requested.connect(self._on_login_requested)
        window.language_selected.connect(self._on_language_selected)
        window.window_closed.connect(self._on_window_closed)
        window.position_changed.connect(self._on_position_changed)
        window.size_changed.connect(self._on_size_changed)
        window.command_delete_requested.connect(self._on_command_delete_requested)
        window.command_search_requested.connect(self._on_command_search_requested)
        window.add_command_requested.connect(self._on_add_command_requested)

        self._windows[note.note_id] = window
        window.show()

        return window

    def open_saved_notes(self) -> list[StickyNoteWindow]:
        windows = []
        for note in self._session_manager.get_notes():
            if note.note_id in self._windows:
                continue
            note.sort_items()
            windows.append(self.open_note_window(note))
        return windows

    def _on_always_on_top_changed(self, note: Note, value: bool) -> None:
        self._session_manager.set_note_always_on_top(note, value)

    def _on_position_changed(self, note: Note, x: int, y: int) -> None:
        self._session_manager.move_note(note, x, y)

    def _on_size_changed(self, note: Note, width: int, height: int) -> None:
        self._session_manager.resize_note(note, width, height)

    def _on_language_selected(self, note: Note, language_id: int) -> None:
        self._session_manager.set_note_language(note, language_id)
        window = self._windows.get(note.note_id)
        if window is not None:
            window.refresh_commands()
            window.refresh_language()

    def _on_new_note_requested(self, note: Note) -> None:
        new_note = self._session_manager.create_note()
        if new_note is None:
            self._windows[note.note_id].show_message(
                "Note limit", "Maximum number of notes reached."
            )
            return
        self.open_note_window(new_note)

    def _on_command_search_requested(self, note: Note, keyword: str) -> None:
        window = self._windows.get(note.note_id)
        if window is None:
            return
        results = self._session_manager.search_commands(note.language_id, keyword)
        window.show_search_results(results)
        #in_note = {cmd.command_id for cmd in note.commands}
        #window.show_search_results([c for c in results if c.command_id not in in_note])

    def _on_add_command_requested(self, note: Note, command: Command) -> None:
        self._session_manager.add_command_to_note(note, command)
        window = self._windows.get(note.note_id)
        if window is not None:
            window.refresh_commands()

    def _on_command_delete_requested(self, note: Note, command: Command) -> None:
        self._session_manager.remove_command_from_note(note, command)
        window = self._windows.get(note.note_id)
        if window is not None:
            window.refresh_commands()

    def _on_delete_requested(self, note: Note) -> None:
        self._session_manager.remove_note(note.note_id)
        window = self._windows.get(note.note_id, None)
        if window is not None:
            window.close()

    def _on_login_requested(self) -> None:
        pass
    
    def _on_window_closed(self, note: Note) -> None:
        self._windows.pop(note.note_id, None)
        if not self._windows and self._on_all_windows_closed:
            self._on_all_windows_closed()
