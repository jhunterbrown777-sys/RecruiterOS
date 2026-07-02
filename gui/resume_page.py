from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
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
        self.detail_content.setReadOnly(True)
        details_layout.addWidget(self.detail_content)

        details_panel.setLayout(details_layout)
        return details_panel

    def refresh(self):
        self.resume_list.clear()

        for resume in self.controller.get_resumes():
            item = QListWidgetItem(self._list_item_text(resume))
            item.setData(Qt.ItemDataRole.UserRole, resume)
            self.resume_list.addItem(item)

        self.update_details()

    def update_details(self):
        selected = self.resume_list.selectedItems()

        if not selected:
            self._show_placeholder()
            return

        resume = selected[0].data(Qt.ItemDataRole.UserRole)
        self._show_details(resume)

    def _list_item_text(self, resume) -> str:
        return f"{resume.title} (v{resume.version})"

    def _show_placeholder(self, message: str = "Select a Resume to see details."):
        self.details_placeholder.setText(message)
        self.details_placeholder.setVisible(True)

        for widget in (self.detail_title, self.detail_version, self.detail_dates, self.detail_content):
            widget.setVisible(False)

    def _show_details(self, resume):
        self.details_placeholder.setVisible(False)

        self.detail_title.setText(f"Title: {resume.title}")
        self.detail_version.setText(f"Version: {resume.version}")
        self.detail_dates.setText(
            f"Created: {resume.created_at.strftime('%Y-%m-%d %H:%M')}  |  "
            f"Updated: {resume.updated_at.strftime('%Y-%m-%d %H:%M')}"
        )
        self.detail_content.setPlainText(resume.content or "No content yet.")

        for widget in (self.detail_title, self.detail_version, self.detail_dates, self.detail_content):
            widget.setVisible(True)
