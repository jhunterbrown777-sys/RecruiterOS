from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QFrame,
)

from models.document import DOCUMENT_TYPES


class DocumentPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        root = QVBoxLayout()

        header = QLabel("Documents")
        header.setObjectName("PageTitle")

        subtitle = QLabel("Library of certificates, portfolio pieces, and other artifacts")
        subtitle.setObjectName("PageSubtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout()

        panel_title = QLabel("Library")
        panel_title.setObjectName("SectionTitle")

        self.document_list = QListWidget()
        self.document_list.itemSelectionChanged.connect(self.update_details)

        self.document_list_empty_state = QLabel("No documents yet. Create one below.")
        self.document_list_empty_state.setObjectName("PageSubtitle")

        panel_layout.addWidget(panel_title)
        panel_layout.addWidget(self.document_list)
        panel_layout.addWidget(self.document_list_empty_state)

        panel.setLayout(panel_layout)
        root.addWidget(panel)

        root.addWidget(self.build_details_panel())
        root.addWidget(self.build_create_panel())

        self._current_document_id = None

        self.setLayout(root)
        self.refresh()

    def build_details_panel(self) -> QFrame:
        details_panel = QFrame()
        details_panel.setObjectName("Panel")
        details_layout = QVBoxLayout()

        details_title = QLabel("Details")
        details_title.setObjectName("SectionTitle")
        details_layout.addWidget(details_title)

        self.details_placeholder = QLabel("Select a Document to see details.")
        self.details_placeholder.setObjectName("PageSubtitle")
        details_layout.addWidget(self.details_placeholder)

        self.detail_title_label = QLabel("Title")
        self.detail_title_input = QLineEdit()
        self.detail_type_label = QLabel("Type")
        self.detail_type_combo = QComboBox()
        self.detail_type_combo.addItems(DOCUMENT_TYPES)
        self.detail_version = QLabel("")
        self.detail_dates = QLabel("")

        for widget in (
            self.detail_title_label,
            self.detail_title_input,
            self.detail_type_label,
            self.detail_type_combo,
            self.detail_version,
            self.detail_dates,
        ):
            details_layout.addWidget(widget)

        self.detail_content = QTextEdit()
        details_layout.addWidget(self.detail_content)

        self.save_content_button = QPushButton("Save Changes")
        self.save_content_button.clicked.connect(self.save_document_content)
        details_layout.addWidget(self.save_content_button)

        self.duplicate_button = QPushButton("Duplicate as New Version")
        self.duplicate_button.clicked.connect(self.duplicate_document)
        details_layout.addWidget(self.duplicate_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_document)
        details_layout.addWidget(self.delete_button)

        self.edit_result = QLabel("")
        self.edit_result.setObjectName("PageSubtitle")
        details_layout.addWidget(self.edit_result)

        details_panel.setLayout(details_layout)
        return details_panel

    def build_create_panel(self) -> QFrame:
        create_panel = QFrame()
        create_panel.setObjectName("Panel")
        create_layout = QVBoxLayout()

        create_title = QLabel("Create Document")
        create_title.setObjectName("SectionTitle")
        create_layout.addWidget(create_title)

        title_label = QLabel("Title")
        create_layout.addWidget(title_label)

        self.new_title_input = QLineEdit()
        self.new_title_input.textChanged.connect(self._update_create_button_state)
        create_layout.addWidget(self.new_title_input)

        type_label = QLabel("Type")
        create_layout.addWidget(type_label)

        self.new_type_combo = QComboBox()
        self.new_type_combo.addItems(DOCUMENT_TYPES)
        create_layout.addWidget(self.new_type_combo)

        content_label = QLabel("Content")
        create_layout.addWidget(content_label)

        self.new_content_input = QTextEdit()
        create_layout.addWidget(self.new_content_input)

        self.create_save_button = QPushButton("Save")
        self.create_save_button.setEnabled(False)
        self.create_save_button.clicked.connect(self.create_document)
        create_layout.addWidget(self.create_save_button)

        self.create_result = QLabel("")
        self.create_result.setObjectName("PageSubtitle")
        create_layout.addWidget(self.create_result)

        create_panel.setLayout(create_layout)
        return create_panel

    def refresh(self):
        self.create_result.setText("")
        self.document_list.clear()

        for document in self.controller.get_documents():
            item = QListWidgetItem(self._list_item_text(document))
            item.setData(Qt.ItemDataRole.UserRole, document)
            self.document_list.addItem(item)

        self.document_list_empty_state.setVisible(self.document_list.count() == 0)

        self.update_details()

    def _update_create_button_state(self):
        self.create_save_button.setEnabled(bool(self.new_title_input.text().strip()))

    def create_document(self):
        title = self.new_title_input.text().strip()

        if not title:
            self.create_result.setText("Title is required.")
            return

        document_type = self.new_type_combo.currentText()
        content = self.new_content_input.toPlainText()
        document = self.controller.create_document(title, document_type, content)

        self.new_title_input.clear()
        self.new_content_input.clear()

        self.refresh()
        self._select_document(document.id)
        self.create_result.setText(f"Created: {document.title}")

    def _select_document(self, document_id: int):
        for index in range(self.document_list.count()):
            item = self.document_list.item(index)
            document = item.data(Qt.ItemDataRole.UserRole)

            if document.id == document_id:
                item.setSelected(True)
                self.document_list.setCurrentItem(item)
                break

    def update_details(self):
        self.edit_result.setText("")
        selected = self.document_list.selectedItems()

        if not selected:
            if self.document_list.count() == 0:
                self._show_placeholder("No documents to select yet.")
            else:
                self._show_placeholder()
            return

        document = selected[0].data(Qt.ItemDataRole.UserRole)
        self._show_details(document)

    def save_document_content(self):
        if self._current_document_id is None:
            return

        title = self.detail_title_input.text().strip()

        if not title:
            self.edit_result.setText("Title is required.")
            return

        document_type = self.detail_type_combo.currentText()
        content = self.detail_content.toPlainText()
        updated = self.controller.update_document_content(self._current_document_id, title, document_type, content)

        self.refresh()
        self._select_document(updated.id)
        self.edit_result.setText(f"Saved: {updated.title}")

    def duplicate_document(self):
        if self._current_document_id is None:
            return

        new_document = self.controller.duplicate_document(self._current_document_id)

        self.refresh()
        self._select_document(new_document.id)
        self.edit_result.setText(f"Duplicated as version {new_document.version}: {new_document.title}")

    def delete_document(self):
        if self._current_document_id is None:
            return

        self.controller.delete_document(self._current_document_id)
        self.refresh()
        self.edit_result.setText("Document deleted.")

    def _list_item_text(self, document) -> str:
        return f"{document.title} — {document.document_type} (v{document.version})"

    def _show_placeholder(self, message: str = "Select a Document to see details."):
        self._current_document_id = None
        self.details_placeholder.setText(message)
        self.details_placeholder.setVisible(True)

        for widget in (
            self.detail_title_label,
            self.detail_title_input,
            self.detail_type_label,
            self.detail_type_combo,
            self.detail_version,
            self.detail_dates,
            self.detail_content,
            self.save_content_button,
            self.duplicate_button,
            self.delete_button,
        ):
            widget.setVisible(False)

    def _show_details(self, document):
        self._current_document_id = document.id
        self.details_placeholder.setVisible(False)

        self.detail_title_input.setText(document.title)
        self.detail_type_combo.setCurrentText(document.document_type)
        self.detail_version.setText(f"Version: {document.version}")
        self.detail_dates.setText(
            f"Created: {document.created_at.strftime('%Y-%m-%d %H:%M')}  |  "
            f"Updated: {document.updated_at.strftime('%Y-%m-%d %H:%M')}"
        )
        self.detail_content.setPlainText(document.content or "")

        for widget in (
            self.detail_title_label,
            self.detail_title_input,
            self.detail_type_label,
            self.detail_type_combo,
            self.detail_version,
            self.detail_dates,
            self.detail_content,
            self.save_content_button,
            self.duplicate_button,
            self.delete_button,
        ):
            widget.setVisible(True)
