import html
from collections.abc import Callable

from PySide6.QtCore import QEvent, QModelIndex, QPoint, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCompleter,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cheatsheet.domain.models import Note, Command


class StickyNoteWindow(QWidget):
    add_command_requested = Signal(Note, Command)
    new_note_requested = Signal(Note)
    delete_requested = Signal(Note)
    login_requested = Signal()
    window_closed = Signal(Note)
    language_dialog_requested = Signal(Note)
    # (note, is_always_on_top)
    always_on_top_changed = Signal(Note, bool)
    # (note, new_x, new_y)
    position_changed = Signal(Note, int, int)
    # (note, new_width, new_height)
    size_changed = Signal(Note, int, int)
    # (note, search_keyword)
    command_search_requested = Signal(Note, str)
    # (note, command)
    command_delete_requested = Signal(Note, Command)

    _GEOMETRY_SAVE_DEBOUNCE_MS = 400

    # Transparent band around the frame: layout margin and resize grab area
    _RESIZE_MARGIN = 10

    _CURSORS = {
        Qt.Edge.LeftEdge: Qt.CursorShape.SizeHorCursor,
        Qt.Edge.RightEdge: Qt.CursorShape.SizeHorCursor,
        Qt.Edge.TopEdge: Qt.CursorShape.SizeVerCursor,
        Qt.Edge.BottomEdge: Qt.CursorShape.SizeVerCursor,
        Qt.Edge.LeftEdge | Qt.Edge.TopEdge: Qt.CursorShape.SizeFDiagCursor,
        Qt.Edge.RightEdge | Qt.Edge.BottomEdge: Qt.CursorShape.SizeFDiagCursor,
        Qt.Edge.RightEdge | Qt.Edge.TopEdge: Qt.CursorShape.SizeBDiagCursor,
        Qt.Edge.LeftEdge | Qt.Edge.BottomEdge: Qt.CursorShape.SizeBDiagCursor,
    }

    def __init__(self, note: Note, language_name: str | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self._note = note
        self._position_save_timer = self._create_debounce_timer(callback=self._emit_position_changed)
        self._size_save_timer = self._create_debounce_timer(callback=self._emit_size_changed)
        self._init_ui()
        self._load_note_data()
        self.set_language_header(language_name=language_name)


    def _init_ui(self) -> None:
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self._note.config.is_always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(self._note.width, self._note.height)
        self.setMinimumSize(Note.MIN_WIDTH, Note.MIN_HEIGHT)
        self.setMouseTracking(True)
        self.move(self._note.pos_x, self._note.pos_y)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            self._RESIZE_MARGIN, self._RESIZE_MARGIN, self._RESIZE_MARGIN, self._RESIZE_MARGIN
        )

        self._container_frame = QFrame()
        self._container_frame.setObjectName("containerFrame")
        self._container_frame.setCursor(Qt.CursorShape.ArrowCursor)
        container_layout = QVBoxLayout(self._container_frame)

        header_layout = QHBoxLayout()

        # Buttons
        self._btn_menu = QPushButton("≡")
        self._btn_menu.setObjectName("btnMenu")
        self._btn_menu.setFixedSize(20, 20)
        self._btn_menu.clicked.connect(self._on_menu_clicked)

        self._btn_close = QPushButton("✕")
        self._btn_close.setObjectName("btnClose")
        self._btn_close.setFixedSize(20, 20)
        self._btn_close.clicked.connect(self.close)

        self._btn_pin = QPushButton("\uE718")
        self._btn_pin.setObjectName("btnPin")
        self._btn_pin.setFixedSize(20, 20)
        self._btn_pin.setCheckable(True)
        self._btn_pin.setChecked(self._note.config.is_always_on_top)
        self._btn_pin.setToolTip("Keep on top")
        self._btn_pin.toggled.connect(self._on_pin_toggled)

        # Search
        self._lbl_language = QLabel()
        self._lbl_language.setObjectName("lblLanguage")

        self._search_input = QLineEdit()
        self._search_input.setObjectName("searchInput")
        self._search_input.setFixedHeight(20)
        self._search_input.textChanged.connect(self._on_search_text_changed)

        self._completer_model = QStandardItemModel(self)
        self._completer = QCompleter(self._completer_model, self)
        self._completer.setCompletionMode(
            QCompleter.CompletionMode.UnfilteredPopupCompletion
        )
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.activated[QModelIndex].connect(self._on_completion_activated)
        self._completer.setWidget(self._search_input)
        self._completer.popup().setObjectName("completerPopup")
        self._search_input.installEventFilter(self)

        header_layout.addWidget(self._btn_menu)
        header_layout.addWidget(self._lbl_language)
        header_layout.addWidget(self._search_input)
        header_layout.addWidget(self._btn_pin)
        header_layout.addWidget(self._btn_close)

        # Commands
        self._command_list = QListWidget()
        self._command_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._command_list.customContextMenuRequested.connect(self._on_command_context_menu)
        self._command_list.setObjectName("commandList")
        self._command_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._command_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        container_layout.addLayout(header_layout)
        container_layout.addWidget(self._command_list)
        main_layout.addWidget(self._container_frame)

    # Public interface
    def set_language_header(self, language_name: str | None) -> None:
        if language_name is None:
            self._lbl_language.setText("No language")
            self._search_input.setReadOnly(True)
            self._search_input.setPlaceholderText("Select a language first")
            return

        self._lbl_language.setText(language_name)
        self._search_input.setReadOnly(False)
        self._search_input.setPlaceholderText("Search commands")

    def refresh_commands(self) -> None:
        self._load_note_data()

    def show_search_results(self, commands: list[Command]) -> None:
        self._completer_model.clear()

        for command in commands:
            item = QStandardItem(f"{command.name} : {command.description}")
            item.setData(command, Qt.ItemDataRole.UserRole)
            self._completer_model.appendRow(item)

        if not commands:
            self._completer.popup().hide()
            return

        self._completer.complete()

    def show_message(self, title: str, text: str) -> None:
        QMessageBox.warning(self, title, text)

    # Command list
    def _load_note_data(self) -> None:
        self._command_list.clear()

        for command in self._note.commands:
            item = QListWidgetItem(f"{command.name} : {command.description}")
            item.setData(Qt.ItemDataRole.UserRole, command)
            if command.examples:
                tooltip_parts = []
                for example in command.examples:
                    tooltip_parts.append(
                        f"<div style=\"font-family: Consolas, monospace; color: #a6e3a1;\">{html.escape(example.code)}</div>"
                    )
                    if example.comment:
                        tooltip_parts.append(
                            f"<div style=\"color: #6c7086; margin-bottom: 6px;\">{html.escape(example.comment)}</div>"
                        )
                item.setToolTip("".join(tooltip_parts))
            else:
                item.setToolTip("-")
            self._command_list.addItem(item)

    def _on_command_context_menu(self, pos: QPoint) -> None:
        item = self._command_list.itemAt(pos)
        if item is None:
            return
        command = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu(self)
        remove_action = menu.addAction("Remove from Note")
        if menu.exec(self._command_list.viewport().mapToGlobal(pos)) is remove_action:
            self.command_delete_requested.emit(self._note, command)

    # Search
    def _on_search_text_changed(self, text: str) -> None:
        keyword = text.strip()
        if not keyword:
            self._completer.popup().hide()
            return
        self.command_search_requested.emit(self._note, keyword)

    def _on_completion_activated(self, index: QModelIndex) -> None:
        command = index.data(Qt.ItemDataRole.UserRole)
        if command is None:
            return
        self.add_command_requested.emit(self._note, command)
        self._search_input.clear()

    def eventFilter(self, watched, event) -> bool:
        if (
            watched is self._search_input
            and event.type() == QEvent.Type.MouseButtonPress
            and self._note.language_id is None
        ):
            self._on_select_language()
            return True
        return super().eventFilter(watched, event)

    # Header
    def _on_menu_clicked(self) -> None:
        menu = QMenu(self)
        #menu.addAction("Log In", self._on_login)
        menu.addAction("New Note", self._on_new_note)
        menu.addAction("Select Language", self._on_select_language)
        menu.addAction("Delete This Note", self._on_delete)

        pos = self._btn_menu.mapToGlobal(self._btn_menu.rect().bottomLeft())
        menu.exec(pos)

    def _on_new_note(self) -> None:
        self.new_note_requested.emit(self._note)

    def _on_select_language(self) -> None:
        self.language_dialog_requested.emit(self._note)

    def _on_delete(self) -> None:
        self.delete_requested.emit(self._note)

    def _on_login(self) -> None:
        self.login_requested.emit()

    def _on_pin_toggled(self, checked: bool) -> None:
        geometry = self.geometry()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, checked)
        self.setGeometry(geometry)
        self.show()
        self.always_on_top_changed.emit(self._note, checked)

    # Geometry persistence
    def _create_debounce_timer(self, callback: Callable[[], None]) -> QTimer:
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(self._GEOMETRY_SAVE_DEBOUNCE_MS)
        timer.timeout.connect(callback)
        return timer

    def moveEvent(self, event) -> None:
        if self.isVisible():
            self._position_save_timer.start()
        super().moveEvent(event)

    def resizeEvent(self, event) -> None:
        if self.isVisible():
            self._size_save_timer.start()
        super().resizeEvent(event)

    def _emit_position_changed(self) -> None:
        self.position_changed.emit(self._note, self.x(), self.y())

    def _emit_size_changed(self) -> None:
        self.size_changed.emit(self._note, self.width(), self.height())

    def closeEvent(self, event) -> None:
        if self._position_save_timer.isActive():
            self._position_save_timer.stop()
            self._emit_position_changed()
        if self._size_save_timer.isActive():
            self._size_save_timer.stop()
            self._emit_size_changed()
        self.window_closed.emit(self._note)
        super().closeEvent(event)

    # Frameless window
    def _get_edge(self, pos: QPoint) -> Qt.Edge:
        rect = self.rect()
        edge = Qt.Edge(0)

        if pos.x() <= self._RESIZE_MARGIN:
            edge |= Qt.Edge.LeftEdge
        elif pos.x() >= rect.width() - self._RESIZE_MARGIN:
            edge |= Qt.Edge.RightEdge

        if pos.y() <= self._RESIZE_MARGIN:
            edge |= Qt.Edge.TopEdge
        elif pos.y() >= rect.height() - self._RESIZE_MARGIN:
            edge |= Qt.Edge.BottomEdge

        return edge

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return

        handle = self.windowHandle()
        if handle is None:
            return

        edge = self._get_edge(event.position().toPoint())
        if edge:
            handle.startSystemResize(edge)
        else:
            handle.startSystemMove()

        event.accept()

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            return

        edge = self._get_edge(event.position().toPoint())
        if edge:
            self.setCursor(self._CURSORS[edge])
        else:
            self.unsetCursor()

    def leaveEvent(self, event) -> None:
        self.unsetCursor()
