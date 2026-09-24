from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cheatsheet.domain.models import Language


class LanguageSearchDialog(QDialog):
    def __init__(self, languages: list[Language], parent: QWidget | None = None):
        super().__init__(parent)
        self._languages = languages
        self._selected_language_id: int | None = None
        self._init_ui()
        self._populate_results(self._languages)
        self._search_input.setFocus()

    @property
    def selected_language_id(self) -> int | None:
        return self._selected_language_id

    def _init_ui(self) -> None:
        # Window
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setObjectName("languageSearchDialog")
        self.setWindowTitle("Select Language")
        self.setFixedSize(260, 300)

        # Header
        self._lbl_title = QLabel("Select Language")

        self._btn_close = QPushButton("✕")
        self._btn_close.setObjectName("btnClose")
        self._btn_close.setFixedSize(20, 20)
        self._btn_close.clicked.connect(self.close)

        # Search bar
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Type to search...")
        self._search_input.textChanged.connect(self._on_search_text_changed)

        # Language list
        self._results_list = QListWidget()
        self._results_list.itemClicked.connect(self._on_item_clicked)

        # Layout
        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self._lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self._btn_close)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self._search_input)
        main_layout.addWidget(self._results_list)

    def _populate_results(self, languages: list[Language]) -> None:
        self._results_list.clear()
        for language in languages:
            item = QListWidgetItem(language.name)
            item.setData(Qt.ItemDataRole.UserRole, language)
            self._results_list.addItem(item)

    def _on_search_text_changed(self, text: str) -> None:
        keyword = text.strip().lower()
        matches = []
        if not keyword:
            matches = self._languages
        else:
            for language in self._languages:
                if keyword in language.name.lower():
                    matches.append(language)
        self._populate_results(matches)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        language: Language = item.data(Qt.ItemDataRole.UserRole)
        self._selected_language_id = language.language_id
        self.accept()
