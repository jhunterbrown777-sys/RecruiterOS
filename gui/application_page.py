from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QFrame,
)

from models.application import APPLICATION_STATUSES


class ApplicationPage(QWidget):
    open_package_requested = Signal(int)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        root = QVBoxLayout()

        header = QLabel("Applications")
        header.setObjectName("PageTitle")

        subtitle = QLabel("Track formally pursued Opportunities through to a decision")
        subtitle.setObjectName("PageSubtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout()

        panel_title = QLabel("Applications")
        panel_title.setObjectName("SectionTitle")

        self.application_list = QListWidget()
        self.application_list.itemSelectionChanged.connect(self.update_details)

        self.application_list_empty_state = QLabel(
            "No applications yet. Create one below from an Opportunity."
        )
        self.application_list_empty_state.setObjectName("PageSubtitle")

        panel_layout.addWidget(panel_title)
        panel_layout.addWidget(self.application_list)
        panel_layout.addWidget(self.application_list_empty_state)

        panel.setLayout(panel_layout)
        root.addWidget(panel)

        root.addWidget(self.build_details_panel())
        root.addWidget(self.build_create_panel())

        self._current_application_id = None

        self.setLayout(root)
        self.refresh()

    def build_details_panel(self) -> QFrame:
        details_panel = QFrame()
        details_panel.setObjectName("Panel")
        details_layout = QVBoxLayout()

        details_title = QLabel("Details")
        details_title.setObjectName("SectionTitle")
        details_layout.addWidget(details_title)

        self.details_placeholder = QLabel("Select an Application to see details.")
        self.details_placeholder.setObjectName("PageSubtitle")
        details_layout.addWidget(self.details_placeholder)

        self.detail_job_title = QLabel("")
        self.detail_company = QLabel("")
        self.detail_dates = QLabel("")

        for label in (self.detail_job_title, self.detail_company, self.detail_dates):
            details_layout.addWidget(label)

        status_label = QLabel("Status")
        status_label.setObjectName("SectionTitle")
        details_layout.addWidget(status_label)

        self.status_combo = QComboBox()
        self.status_combo.addItems(APPLICATION_STATUSES)
        details_layout.addWidget(self.status_combo)

        self.save_status_button = QPushButton("Save Status")
        self.save_status_button.clicked.connect(self.save_status)
        details_layout.addWidget(self.save_status_button)

        resume_label = QLabel("Resume")
        resume_label.setObjectName("SectionTitle")
        details_layout.addWidget(resume_label)

        self.resume_combo = QComboBox()
        details_layout.addWidget(self.resume_combo)

        self.save_resume_button = QPushButton("Link Resume")
        self.save_resume_button.clicked.connect(self.save_resume_link)
        details_layout.addWidget(self.save_resume_button)

        cover_letter_label = QLabel("Cover Letter")
        cover_letter_label.setObjectName("SectionTitle")
        details_layout.addWidget(cover_letter_label)

        self.cover_letter_combo = QComboBox()
        details_layout.addWidget(self.cover_letter_combo)

        self.save_cover_letter_button = QPushButton("Link Cover Letter")
        self.save_cover_letter_button.clicked.connect(self.save_cover_letter_link)
        details_layout.addWidget(self.save_cover_letter_button)

        notes_label = QLabel("Notes")
        notes_label.setObjectName("SectionTitle")
        details_layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        details_layout.addWidget(self.notes_input)

        self.save_notes_button = QPushButton("Save Notes")
        self.save_notes_button.clicked.connect(self.save_notes)
        details_layout.addWidget(self.save_notes_button)

        self.view_package_button = QPushButton("View Application Package")
        self.view_package_button.clicked.connect(self._emit_open_package)
        details_layout.addWidget(self.view_package_button)

        self.edit_result = QLabel("")
        self.edit_result.setObjectName("PageSubtitle")
        details_layout.addWidget(self.edit_result)

        details_panel.setLayout(details_layout)
        return details_panel

    def build_create_panel(self) -> QFrame:
        create_panel = QFrame()
        create_panel.setObjectName("Panel")
        create_layout = QVBoxLayout()

        create_title = QLabel("Create Application")
        create_title.setObjectName("SectionTitle")
        create_layout.addWidget(create_title)

        self.opportunity_combo = QComboBox()
        create_layout.addWidget(self.opportunity_combo)

        self.create_button = QPushButton("Create Application")
        self.create_button.clicked.connect(self.create_application)
        create_layout.addWidget(self.create_button)

        self.create_empty_state = QLabel("No Opportunities with a resolvable Job are available yet.")
        self.create_empty_state.setObjectName("PageSubtitle")
        create_layout.addWidget(self.create_empty_state)

        self.create_result = QLabel("")
        self.create_result.setObjectName("PageSubtitle")
        create_layout.addWidget(self.create_result)

        create_panel.setLayout(create_layout)
        return create_panel

    def refresh(self):
        self.create_result.setText("")
        self.application_list.clear()

        for summary in self.controller.get_applications():
            item = QListWidgetItem(self._list_item_text(summary))
            item.setData(Qt.ItemDataRole.UserRole, summary)
            self.application_list.addItem(item)

        self.application_list_empty_state.setVisible(self.application_list.count() == 0)

        self._refresh_opportunity_combo()
        self.update_details()

    def _refresh_opportunity_combo(self):
        self.opportunity_combo.clear()

        for opportunity, job in self.controller.get_opportunities():
            if job is None:
                continue

            self.opportunity_combo.addItem(f"{job.title} — {job.company}", opportunity.id)

        has_opportunities = self.opportunity_combo.count() > 0
        self.opportunity_combo.setVisible(has_opportunities)
        self.create_button.setEnabled(has_opportunities)
        self.create_empty_state.setVisible(not has_opportunities)

    def select_opportunity(self, opportunity_id: int):
        """Best-effort preselect an Opportunity in the create combo."""
        index = self.opportunity_combo.findData(opportunity_id)

        if index >= 0:
            self.opportunity_combo.setCurrentIndex(index)

    def create_application(self):
        opportunity_id = self.opportunity_combo.currentData()

        if opportunity_id is None:
            return

        application = self.controller.create_application_for_opportunity(opportunity_id)

        self.refresh()
        self._select_application(application.id)
        self.create_result.setText(f"Application ready (status: {application.status}).")

    def select_application(self, application_id: int):
        """Public entry point for other pages to preselect an Application here."""
        self._select_application(application_id)

    def _select_application(self, application_id: int):
        for index in range(self.application_list.count()):
            item = self.application_list.item(index)
            summary = item.data(Qt.ItemDataRole.UserRole)

            if summary.application.id == application_id:
                item.setSelected(True)
                self.application_list.setCurrentItem(item)
                break

    def update_details(self):
        self.edit_result.setText("")
        selected = self.application_list.selectedItems()

        if not selected:
            if self.application_list.count() == 0:
                self._show_placeholder("No applications to select yet.")
            else:
                self._show_placeholder()
            return

        summary = selected[0].data(Qt.ItemDataRole.UserRole)
        self._show_details(summary)

    def save_status(self):
        if self._current_application_id is None:
            return

        new_status = self.status_combo.currentText()
        self.controller.update_application_status(self._current_application_id, new_status)

        self.refresh()
        self._select_application(self._current_application_id)
        self.edit_result.setText(f"Status saved: {new_status}")

    def save_resume_link(self):
        if self._current_application_id is None:
            return

        resume_id = self.resume_combo.currentData()
        self.controller.attach_resume_to_application(self._current_application_id, resume_id)

        self.refresh()
        self._select_application(self._current_application_id)
        self.edit_result.setText("Resume linked.")

    def save_cover_letter_link(self):
        if self._current_application_id is None:
            return

        cover_letter_id = self.cover_letter_combo.currentData()
        self.controller.attach_cover_letter_to_application(self._current_application_id, cover_letter_id)

        self.refresh()
        self._select_application(self._current_application_id)
        self.edit_result.setText("Cover letter linked.")

    def save_notes(self):
        if self._current_application_id is None:
            return

        notes = self.notes_input.toPlainText()
        self.controller.update_application_notes(self._current_application_id, notes)

        self.refresh()
        self._select_application(self._current_application_id)
        self.edit_result.setText("Notes saved.")

    def _emit_open_package(self):
        if self._current_application_id is None:
            return

        self.open_package_requested.emit(self._current_application_id)

    def _list_item_text(self, summary) -> str:
        if summary.job is None:
            return f"(Job unavailable) ({summary.application.status})"

        return f"{summary.job.title} — {summary.job.company} ({summary.application.status})"

    def _show_placeholder(self, message: str = "Select an Application to see details."):
        self._current_application_id = None
        self.details_placeholder.setText(message)
        self.details_placeholder.setVisible(True)

        for widget in (
            self.detail_job_title,
            self.detail_company,
            self.detail_dates,
            self.status_combo,
            self.save_status_button,
            self.resume_combo,
            self.save_resume_button,
            self.cover_letter_combo,
            self.save_cover_letter_button,
            self.notes_input,
            self.save_notes_button,
            self.view_package_button,
        ):
            widget.setVisible(False)

    def _show_details(self, summary):
        self._current_application_id = summary.application.id
        self.details_placeholder.setVisible(False)

        job = summary.job
        self.detail_job_title.setText(f"Job: {job.title if job else 'Unavailable'}")
        self.detail_company.setText(f"Company: {job.company if job else 'Unavailable'}")
        self.detail_dates.setText(
            f"Created: {summary.application.created_at.strftime('%Y-%m-%d %H:%M')}  |  "
            f"Updated: {summary.application.updated_at.strftime('%Y-%m-%d %H:%M')}"
        )

        index = self.status_combo.findText(summary.application.status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

        self._refresh_resume_combo(summary.application.resume_id)
        self._refresh_cover_letter_combo(summary.application.cover_letter_id)
        self.notes_input.setPlainText(summary.application.notes or "")

        for widget in (
            self.detail_job_title,
            self.detail_company,
            self.detail_dates,
            self.status_combo,
            self.save_status_button,
            self.resume_combo,
            self.save_resume_button,
            self.cover_letter_combo,
            self.save_cover_letter_button,
            self.notes_input,
            self.save_notes_button,
            self.view_package_button,
        ):
            widget.setVisible(True)

    def _refresh_resume_combo(self, selected_resume_id):
        self.resume_combo.clear()
        self.resume_combo.addItem("None", None)

        for resume in self.controller.get_resumes():
            self.resume_combo.addItem(f"{resume.title} (v{resume.version})", resume.id)

        index = self.resume_combo.findData(selected_resume_id)
        self.resume_combo.setCurrentIndex(index if index >= 0 else 0)

    def _refresh_cover_letter_combo(self, selected_cover_letter_id):
        self.cover_letter_combo.clear()
        self.cover_letter_combo.addItem("None", None)

        for cover_letter in self.controller.get_cover_letters():
            self.cover_letter_combo.addItem(f"{cover_letter.title} (v{cover_letter.version})", cover_letter.id)

        index = self.cover_letter_combo.findData(selected_cover_letter_id)
        self.cover_letter_combo.setCurrentIndex(index if index >= 0 else 0)
