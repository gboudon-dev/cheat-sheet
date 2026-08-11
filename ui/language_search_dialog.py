from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout

from domain import Language


class LanguageSearchDialog(QDialog):
    def __init__(self, languages: list[Language], parent=None):
        super().__init__(parent)
        self._languages = languages
        self.selected_language_id: int | None = None

        self.setWindowTitle("Select language")
        self.setFixedSize(260, 300)

        layout = QVBoxLayout(self)

        self.lbl_title = QLabel("Select language")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self._on_text_changed)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.search_input)
        layout.addWidget(self.results_list)

        self._apply_styles()
        self._populate_results(self._languages)
        self.search_input.setFocus()

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 4px;
                color: #cdd6f4;
                padding: 4px;
                font-size: 12px;
            }
            QListWidget {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 4px;
                color: #a6e3a1;
                font-size: 12px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 4px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #313244;
                color: #f9e2af;
            }
        """)

    def _populate_results(self, languages: list[Language]) -> None:
        self.results_list.clear()
        for lang in languages:
            item = QListWidgetItem(lang.name)
            item.setData(Qt.ItemDataRole.UserRole, lang)
            self.results_list.addItem(item)

    def _on_text_changed(self, text: str) -> None:
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
