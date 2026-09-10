from domain import Command, Note
from session_manager import SessionManager
from ui.sticky_note import StickyNoteWindow
from ui.language_search_dialog import LanguageSearchDialog
from PySide6.QtWidgets import QDialog


class AppController:
    def __init__(self, session_manager: SessionManager, on_all_windows_closed=None):
        self._session_manager = session_manager
        self._windows: dict[int, StickyNoteWindow] = {}
        self._on_all_windows_closed=on_all_windows_closed

    def open_note_window(self, note: Note) -> StickyNoteWindow:
        language_name = self._get_language_name(note.language_id)
        window = StickyNoteWindow(note=note, language_name=language_name)
        window.always_on_top_changed.connect(self._on_always_on_top_changed)
        window.new_note_requested.connect(self._on_new_note_requested)
        window.delete_requested.connect(self._on_note_delete_requested)
        window.login_requested.connect(self._on_login_requested)
        window.language_dialog_requested.connect(self._on_language_dialog_requested)
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
            note.sort_commands()
            window = self.open_note_window(note)
            windows.append(window)
        return windows

    def _on_language_dialog_requested(self, note: Note) -> None:
        languages = self._session_manager.get_languages()
        window = self._windows[note.note_id]

        dialog = LanguageSearchDialog(languages=languages, parent=window)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_language_id is not None:
            self._apply_language(note, dialog.selected_language_id)

    def _apply_language(self, note: Note, language_id: int) -> None:
        self._session_manager.set_note_language(note, language_id)
        window = self._windows[note.note_id]
        language_name = self._get_language_name(language_id)
        window.set_language_header(language_name)
        window.refresh_commands()

    def _get_language_name(self, language_id: int | None) -> str | None:
        if language_id is None:
            return None

        for lang in self._session_manager.get_languages():
            if lang.language_id == language_id:
                return lang.name

        return None

    def _on_always_on_top_changed(self, note: Note, value: bool) -> None:
        self._session_manager.set_note_always_on_top(note, value)

    def _on_position_changed(self, note: Note, x: int, y: int) -> None:
        self._session_manager.move_note(note, x, y)

    def _on_size_changed(self, note: Note, width: int, height: int) -> None:
        self._session_manager.resize_note(note, width, height)

    def _on_new_note_requested(self, note: Note) -> None:
        new_note = self._session_manager.create_note()
        if new_note is None:
            window = self._windows[note.note_id]
            window.show_message(
                "Note limit", "Maximum number of notes reached."
            )
            return
        self.open_note_window(new_note)

    def _on_command_search_requested(self, note: Note, keyword: str) -> None:
        window = self._windows[note.note_id]
        results = self._session_manager.search_commands(note.language_id, keyword)
        window.show_search_results(results)

    def _on_add_command_requested(self, note: Note, command: Command) -> None:
        self._session_manager.add_command_to_note(note, command)
        window = self._windows[note.note_id]
        window.refresh_commands()

    def _on_command_delete_requested(self, note: Note, command: Command) -> None:
        self._session_manager.remove_command_from_note(note, command)
        window = self._windows[note.note_id]
        window.refresh_commands()

    def _on_note_delete_requested(self, note: Note) -> None:
        window = self._windows.pop(note.note_id)
        self._session_manager.remove_note(note_id=note.note_id)
        window.close()

    def _on_window_closed(self, note: Note) -> None:
        if note.note_id in self._windows:
            if not note.commands:
                self._on_note_delete_requested(note=note)
            else:
                self._windows.pop(note.note_id)

        if not self._windows and self._on_all_windows_closed:
            self._on_all_windows_closed()

    def _on_login_requested(self) -> None:
        pass

