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
)

from cheatsheet.domain.models import Language


class LanguageSearchDialog(QDialog):
    def __init__(self, languages: list[Language], parent=None):
        super().__init__(parent)
        self._languages = languages
        self.selected_language_id: int | None = None
        self._init_ui()
        self._load_languages()

    def _init_ui(self) -> None:
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setObjectName("languageSearchDialog")
        self.setWindowTitle("Select Language")
        self.setFixedSize(260, 300)

        main_layout = QVBoxLayout(self)
        header_layout = QHBoxLayout()

        self._lbl_title = QLabel("Select Language")

        self._btn_close = QPushButton("✕")
        self._btn_close.setObjectName("btnClose")
        self._btn_close.setFixedSize(20, 20)
        self._btn_close.clicked.connect(self.close)

        header_layout.addWidget(self._lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self._btn_close)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Type to search...")
        self._search_input.textChanged.connect(self._on_search_text_changed)

        self._results_list = QListWidget()
        self._results_list.itemClicked.connect(self._on_item_clicked)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self._search_input)
        main_layout.addWidget(self._results_list)

    def _load_languages(self) -> None:
        self._populate_results(self._languages)
        self._search_input.setFocus()

    def _populate_results(self, languages: list[Language]) -> None:
        self._results_list.clear()
        for lang in languages:
            item = QListWidgetItem(lang.name)
            item.setData(Qt.ItemDataRole.UserRole, lang)
            self._results_list.addItem(item)

    def _on_search_text_changed(self, text: str) -> None:
        keyword = text.strip().lower()
        matches = []
        if not keyword:
            matches = self._languages
        else:
            for lang in self._languages:
                if keyword in lang.name.lower():
                    matches.append(lang)
        self._populate_results(matches)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        lang: Language = item.data(Qt.ItemDataRole.UserRole)
        self.selected_language_id = lang.language_id
        self.accept()
