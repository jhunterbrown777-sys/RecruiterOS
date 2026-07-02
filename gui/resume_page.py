from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QFrame,
)


class ResumePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        root = QVBoxLayout()

        header = QLabel("Resume")
        header.setObjectName("PageTitle")

        subtitle = QLabel("Manage your master resume and tailored versions")
        subtitle.setObjectName("PageSubtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout()

        panel_title = QLabel("Resumes")
        panel_title.setObjectName("SectionTitle")

        self.resume_list = QListWidget()
        self.resume_list.itemSelectionChanged.connect(self.update_details)

        panel_layout.addWidget(panel_title)
        panel_layout.addWidget(self.resume_list)

        panel.setLayout(panel_layout)
        root.addWidget(panel)

        root.addWidget(self.build_details_panel())
        root.addWidget(self.build_create_panel())

        self._current_resume_id = None

        self.setLayout(root)
        self.refresh()

    def build_details_panel(self) -> QFrame:
        details_panel = QFrame()
        details_panel.setObjectName("Panel")
        details_layout = QVBoxLayout()

        details_title = QLabel("Details")
        details_title.setObjectName("SectionTitle")
        details_layout.addWidget(details_title)

        self.details_placeholder = QLabel("Select a Resume to see details.")
        self.details_placeholder.setObjectName("PageSubtitle")
        details_layout.addWidget(self.details_placeholder)

        self.detail_title = QLabel("")
        self.detail_version = QLabel("")
        self.detail_dates = QLabel("")

        for label in (self.detail_title, self.detail_version, self.detail_dates):
            details_layout.addWidget(label)

        self.detail_content = QTextEdit()
        details_layout.addWidget(self.detail_content)

        self.save_content_button = QPushButton("Save Changes")
        self.save_content_button.clicked.connect(self.save_resume_content)
        details_layout.addWidget(self.save_content_button)

        self.edit_result = QLabel("")
        self.edit_result.setObjectName("PageSubtitle")
        details_layout.addWidget(self.edit_result)

        details_panel.setLayout(details_layout)
        return details_panel

    def build_create_panel(self) -> QFrame:
        create_panel = QFrame()
        create_panel.setObjectName("Panel")
        create_layout = QVBoxLayout()

        create_title = QLabel("Create Resume")
        create_title.setObjectName("SectionTitle")
        create_layout.addWidget(create_title)

        title_label = QLabel("Title")
        create_layout.addWidget(title_label)

        self.new_title_input = QLineEdit()
        create_layout.addWidget(self.new_title_input)

        content_label = QLabel("Content")
        create_layout.addWidget(content_label)

        self.new_content_input = QTextEdit()
        create_layout.addWidget(self.new_content_input)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.create_resume)
        create_layout.addWidget(save_button)

        self.create_result = QLabel("")
        self.create_result.setObjectName("PageSubtitle")
        create_layout.addWidget(self.create_result)

        create_panel.setLayout(create_layout)
        return create_panel

    def refresh(self):
        self.create_result.setText("")
        self.resume_list.clear()

        for resume in self.controller.get_resumes():
            item = QListWidgetItem(self._list_item_text(resume))
            item.setData(Qt.ItemDataRole.UserRole, resume)
            self.resume_list.addItem(item)

        self.update_details()

    def create_resume(self):
        title = self.new_title_input.text().strip()

        if not title:
            self.create_result.setText("Title is required.")
            return

        content = self.new_content_input.toPlainText()
        resume = self.controller.create_resume(title, content)

        self.new_title_input.clear()
        self.new_content_input.clear()

        self.refresh()
        self._select_resume(resume.id)
        self.create_result.setText(f"Created: {resume.title}")

    def _select_resume(self, resume_id: int):
        for index in range(self.resume_list.count()):
            item = self.resume_list.item(index)
            resume = item.data(Qt.ItemDataRole.UserRole)

            if resume.id == resume_id:
                item.setSelected(True)
                self.resume_list.setCurrentItem(item)
                break

    def update_details(self):
        self.edit_result.setText("")
        selected = self.resume_list.selectedItems()

        if not selected:
            self._show_placeholder()
            return

        resume = selected[0].data(Qt.ItemDataRole.UserRole)
        self._show_details(resume)

    def save_resume_content(self):
        if self._current_resume_id is None:
            return

        content = self.detail_content.toPlainText()
        updated = self.controller.update_resume_content(self._current_resume_id, content)

        self.refresh()
        self._select_resume(updated.id)
        self.edit_result.setText(f"Saved: {updated.title}")

    def _list_item_text(self, resume) -> str:
        return f"{resume.title} (v{resume.version})"

    def _show_placeholder(self, message: str = "Select a Resume to see details."):
        self._current_resume_id = None
        self.details_placeholder.setText(message)
        self.details_placeholder.setVisible(True)

        for widget in (
            self.detail_title,
            self.detail_version,
            self.detail_dates,
            self.detail_content,
            self.save_content_button,
        ):
            widget.setVisible(False)

    def _show_details(self, resume):
        self._current_resume_id = resume.id
        self.details_placeholder.setVisible(False)

        self.detail_title.setText(f"Title: {resume.title}")
        self.detail_version.setText(f"Version: {resume.version}")
        self.detail_dates.setText(
            f"Created: {resume.created_at.strftime('%Y-%m-%d %H:%M')}  |  "
            f"Updated: {resume.updated_at.strftime('%Y-%m-%d %H:%M')}"
        )
        self.detail_content.setPlainText(resume.content or "")

        for widget in (
            self.detail_title,
            self.detail_version,
            self.detail_dates,
            self.detail_content,
            self.save_content_button,
        ):
            widget.setVisible(True)
