from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QAbstractItemView
)
from domain import Note


class StickyNoteWindow(QWidget):
    always_on_top_changed = Signal(Note, bool)

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

    def __init__(self, note: Note, parent=None):
        super().__init__(parent)
        self.note = note
        self._margin = 10
        self._drag_position: QPoint | None = None
        self._init_ui()
        self._load_note_data()

    def _init_ui(self) -> None:
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.note.config.is_always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(400, 220)
        self.setMinimumSize(220, 150)
        self.setMouseTracking(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            self._margin, self._margin, self._margin, self._margin
        )

        self.container_frame = QFrame()
        self.container_frame.setObjectName("containerFrame")
        self.container_frame.setCursor(Qt.CursorShape.ArrowCursor)
        container_layout = QVBoxLayout(self.container_frame)

        header_layout = QHBoxLayout()

        # Buttons
        self.btn_menu = QPushButton("≡")
        self.btn_menu.setObjectName("btnMenu")
        self.btn_menu.setFixedSize(20, 20)
        self.btn_menu.clicked.connect(self._on_menu_clicked)

        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("btnClose")
        self.btn_close.setFixedSize(20, 20)
        self.btn_close.clicked.connect(self.close)

        self.btn_pin = QPushButton("\uE718")
        self.btn_pin.setObjectName("btnPin")
        self.btn_pin.setFixedSize(20, 20)
        self.btn_pin.setCheckable(True)
        self.btn_pin.setChecked(self.note.config.is_always_on_top)
        self.btn_pin.setToolTip("Keep on top")
        self.btn_pin.toggled.connect(self._on_pin_toggled)

        header_layout.addWidget(self.btn_menu)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_pin)
        header_layout.addWidget(self.btn_close)

        # Commands
        self.command_list = QListWidget()
        self.command_list.setObjectName("commandList")
        self.command_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.command_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
       
        container_layout.addLayout(header_layout)
        container_layout.addWidget(self.command_list)
        main_layout.addWidget(self.container_frame)

        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QFrame#containerFrame {
                background-color: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 8px;
            }
            QPushButton#btnMenu, QPushButton#btnClose {
                background: transparent;
                color: #a6adc8;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton#btnClose:hover {
                background-color: #f38ba8;
                color: #11111b;
            }
            QPushButton#btnMenu:hover {
                background-color: #45475a ;
                color: #cdd6f4 ;
            }
            QListWidget#commandList {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 4px;
                color: #a6e3a1;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 4px;
            }
            QListWidget#commandList::item {
                padding: 4px;
                border-radius: 3px;
            }
            QListWidget#commandList::item:hover {
                background-color: #313244;
                color: #f9e2af;
            }
            QPushButton#btnPin {
                background: transparent;
                color: #6c7086;
                border: none;
                border-radius: 3px;
                font-family: 'Segoe Fluent Icons', 'Segoe MDL2 Assets';
                font-size: 11px;
            }
            QPushButton#btnPin:checked {
                color: #f9e2af;
            }
            QPushButton#btnPin:hover {
                background-color: #45475a;
            }
        """)

    def _load_note_data(self) -> None:
        self.command_list.clear()

        for cmd in self.note.commands:
            item = QListWidgetItem(f"{cmd.name} : {cmd.description}")
            item.setData(Qt.ItemDataRole.UserRole, cmd)
            if cmd.example:
                item.setToolTip(cmd.example)
            else:
                item.setToolTip("-")
            self.command_list.addItem(item)

    def _on_menu_clicked(self):
        pass

    def _on_pin_toggled(self, checked: bool) -> None:
        geometry = self.geometry()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, checked)
        self.setGeometry(geometry)
        self.show()
        self.always_on_top_changed.emit(self.note, checked)

    def _get_edge(self, pos: QPoint) -> Qt.Edge:
        rect = self.rect()
        edge = Qt.Edge(0)

        if pos.x() <= self._margin:
            edge |= Qt.Edge.LeftEdge
        elif pos.x() >= rect.width() - self._margin:
            edge |= Qt.Edge.RightEdge

        if pos.y() <= self._margin:
            edge |= Qt.Edge.TopEdge
        elif pos.y() >= rect.height() - self._margin:
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
        elif not handle.startSystemMove():
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        event.accept()

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._drag_position is not None:
                self.move(event.globalPosition().toPoint() - self._drag_position)
                event.accept()
            return

        edge = self._get_edge(event.position().toPoint())
        if edge:
            self.setCursor(self._CURSORS[edge])
        else:
            self.unsetCursor()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_position = None
        event.accept()

    def leaveEvent(self, event) -> None:
        self.unsetCursor()
