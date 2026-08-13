from domain import Note
from session_manager import SessionManager
from ui.sticky_note import StickyNoteWindow


class AppController:
    def __init__(self, session_manager: SessionManager):
        self._session_manager = session_manager
        self._windows: dict[int, StickyNoteWindow] = {}
        self._languages = self._session_manager.get_languages()

    def open_note_window(self, note: Note) -> StickyNoteWindow:
        window = StickyNoteWindow(note=note, languages=self._languages)
        window.always_on_top_changed.connect(self._on_always_on_top_changed)
        window.new_note_requested.connect(self._on_new_note_requested)
        window.delete_requested.connect(self._on_delete_requested)
        window.login_requested.connect(self._on_login_requested)
        window.language_selected.connect(self._on_language_selected)

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

    def _on_language_selected(self, note: Note, language_id: int) -> None:
        self._session_manager.load_default_pack_to_note(note, language_id)
        window = self._windows.get(note.note_id)
        if window is not None:
            window.refresh_commands()

    def _on_new_note_requested(self) -> None:
        note = self._session_manager.create_note()
        self.open_note_window(note)

    def _on_delete_requested(self, note: Note) -> None:
        self._session_manager.remove_note(note.note_id)
        window = self._windows.pop(note.note_id, None)
        if window is not None:
            window.close()

    def _on_login_requested(self) -> None:
        pass
