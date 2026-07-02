from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QFrame,
    QComboBox,
    QPushButton,
)

ALLOWED_STATUSES = [
    "SCOUTED",
    "ASSESSED",
    "APPLYING",
    "APPLIED",
    "INTERVIEWING",
    "OFFER",
    "CLOSED",
]


class OpportunityPage(QWidget):
    resume_generated = Signal(int)
    cover_letter_generated = Signal(int)
    open_resume_workspace_requested = Signal(int)
    open_cover_letter_workspace_requested = Signal(int)
    open_documents_requested = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        root = QVBoxLayout()

        header = QLabel("Opportunities")
        header.setObjectName("PageTitle")

        subtitle = QLabel("Jobs you're tracking")
        subtitle.setObjectName("PageSubtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout()

        panel_title = QLabel("Pipeline")
        panel_title.setObjectName("SectionTitle")

        self.opportunities_list = QListWidget()
        self.opportunities_list.itemSelectionChanged.connect(self.update_details)

        panel_layout.addWidget(panel_title)
        panel_layout.addWidget(self.opportunities_list)

        panel.setLayout(panel_layout)
        root.addWidget(panel)

        root.addWidget(self.build_details_panel())

        self._current_opportunity_id = None

        self.setLayout(root)
        self.refresh()

    def build_details_panel(self) -> QFrame:
        details_panel = QFrame()
        details_panel.setObjectName("Panel")
        details_layout = QVBoxLayout()

        details_title = QLabel("Details")
        details_title.setObjectName("SectionTitle")
        details_layout.addWidget(details_title)

        self.details_placeholder = QLabel("Select an Opportunity to see details.")
        self.details_placeholder.setObjectName("PageSubtitle")
        details_layout.addWidget(self.details_placeholder)

        self.detail_job_title = QLabel("")
        self.detail_company = QLabel("")
        self.detail_location = QLabel("")
        self.detail_source = QLabel("")
        self.detail_status = QLabel("")
        self.detail_dates = QLabel("")

        for label in (
            self.detail_job_title,
            self.detail_company,
            self.detail_location,
            self.detail_source,
            self.detail_status,
            self.detail_dates,
        ):
            details_layout.addWidget(label)

        self.detail_description = QTextEdit()
        self.detail_description.setReadOnly(True)
        details_layout.addWidget(self.detail_description)

        status_label = QLabel("Update Status")
        status_label.setObjectName("SectionTitle")
        details_layout.addWidget(status_label)

        self.status_combo = QComboBox()
        self.status_combo.addItems(ALLOWED_STATUSES)
        details_layout.addWidget(self.status_combo)

        self.save_status_button = QPushButton("Save Status")
        self.save_status_button.clicked.connect(self.save_status)
        details_layout.addWidget(self.save_status_button)

        self.status_save_result = QLabel("")
        self.status_save_result.setObjectName("PageSubtitle")
        details_layout.addWidget(self.status_save_result)

        assessment_title = QLabel("Latest Assessment")
        assessment_title.setObjectName("SectionTitle")
        details_layout.addWidget(assessment_title)

        self.analyze_button = QPushButton("Analyze Opportunity")
        self.analyze_button.clicked.connect(self.analyze_opportunity)
        details_layout.addWidget(self.analyze_button)

        self.assessment_result = QLabel("")
        self.assessment_result.setObjectName("PageSubtitle")
        details_layout.addWidget(self.assessment_result)

        self.assessment_placeholder = QLabel("No Assessment yet.")
        self.assessment_placeholder.setObjectName("PageSubtitle")
        details_layout.addWidget(self.assessment_placeholder)

        self.assessment_score = QLabel("")
        self.assessment_sub_scores = QLabel("")
        self.assessment_recommendation = QLabel("")
        self.assessment_generated_at = QLabel("")

        for label in (
            self.assessment_score,
            self.assessment_sub_scores,
            self.assessment_recommendation,
        ):
            details_layout.addWidget(label)

        self.assessment_reasoning = QTextEdit()
        self.assessment_reasoning.setReadOnly(True)
        details_layout.addWidget(self.assessment_reasoning)

        details_layout.addWidget(self.assessment_generated_at)

        documents_title = QLabel("Documents & Cover Letters")
        documents_title.setObjectName("SectionTitle")
        details_layout.addWidget(documents_title)

        self.generate_resume_button = QPushButton("Generate Resume")
        self.generate_resume_button.clicked.connect(self.generate_resume)
        details_layout.addWidget(self.generate_resume_button)

        self.generate_cover_letter_button = QPushButton("Generate Cover Letter")
        self.generate_cover_letter_button.clicked.connect(self.generate_cover_letter)
        details_layout.addWidget(self.generate_cover_letter_button)

        self.open_resume_workspace_button = QPushButton("Open Resume Workspace")
        self.open_resume_workspace_button.clicked.connect(self.open_resume_workspace)
        details_layout.addWidget(self.open_resume_workspace_button)

        self.open_cover_letter_workspace_button = QPushButton("Open Cover Letter Workspace")
        self.open_cover_letter_workspace_button.clicked.connect(self.open_cover_letter_workspace)
        details_layout.addWidget(self.open_cover_letter_workspace_button)

        self.open_documents_button = QPushButton("Open Documents")
        self.open_documents_button.clicked.connect(self.open_documents_requested.emit)
        details_layout.addWidget(self.open_documents_button)

        self.documents_result = QLabel("")
        self.documents_result.setObjectName("PageSubtitle")
        details_layout.addWidget(self.documents_result)

        details_panel.setLayout(details_layout)
        return details_panel

    def refresh(self):
        self.opportunities_list.clear()

        for opportunity, job in self.controller.get_opportunities():
            item = QListWidgetItem(self._list_item_text(opportunity, job))
            item.setData(Qt.ItemDataRole.UserRole, (opportunity, job))
            self.opportunities_list.addItem(item)

        self.update_details()

    def update_details(self):
        self.status_save_result.setText("")
        self.assessment_result.setText("")
        self.documents_result.setText("")

        selected = self.opportunities_list.selectedItems()

        if not selected:
            self._show_placeholder()
            self._hide_status_editor()
            self.analyze_button.setVisible(False)
            self._hide_assessment_display()
            self._set_documents_buttons_enabled(False)
            return

        opportunity, job = selected[0].data(Qt.ItemDataRole.UserRole)

        if job is None:
            self._show_placeholder("Job details unavailable for this Opportunity.")
            self.analyze_button.setVisible(False)
            self._set_documents_buttons_enabled(False)
        else:
            self._show_details(opportunity, job)
            self.analyze_button.setVisible(True)
            self._set_documents_buttons_enabled(True)

        self._show_status_editor(opportunity)
        self._refresh_assessment_display(opportunity.id)

    def _set_documents_buttons_enabled(self, enabled: bool):
        for button in (
            self.generate_resume_button,
            self.generate_cover_letter_button,
            self.open_resume_workspace_button,
            self.open_cover_letter_workspace_button,
            self.open_documents_button,
        ):
            button.setEnabled(enabled)

    def analyze_opportunity(self):
        if self._current_opportunity_id is None:
            return

        self.analyze_button.setEnabled(False)
        self.assessment_result.setText("Analyzing…")
        QApplication.processEvents()

        try:
            self.controller.analyze_opportunity(self._current_opportunity_id)
            self.assessment_result.setText("Assessment generated.")
        except Exception as error:
            self.assessment_result.setText(f"Analysis failed: {error}")
        finally:
            self.analyze_button.setEnabled(True)

        self._refresh_assessment_display(self._current_opportunity_id)

    def generate_resume(self):
        if self._current_opportunity_id is None:
            return

        self.generate_resume_button.setEnabled(False)
        self.documents_result.setText("Generating resume…")
        QApplication.processEvents()

        try:
            resume = self.controller.generate_resume_for_opportunity(self._current_opportunity_id)
            self.documents_result.setText(f"Generated resume: {resume.title}")
            self.resume_generated.emit(resume.id)
        except Exception as error:
            self.documents_result.setText(f"Resume generation failed: {error}")
        finally:
            self.generate_resume_button.setEnabled(True)

    def generate_cover_letter(self):
        if self._current_opportunity_id is None:
            return

        self.generate_cover_letter_button.setEnabled(False)
        self.documents_result.setText("Generating cover letter…")
        QApplication.processEvents()

        try:
            cover_letter = self.controller.generate_cover_letter_for_opportunity(self._current_opportunity_id)
            self.documents_result.setText(f"Generated cover letter: {cover_letter.title}")
            self.cover_letter_generated.emit(cover_letter.id)
        except Exception as error:
            self.documents_result.setText(f"Cover letter generation failed: {error}")
        finally:
            self.generate_cover_letter_button.setEnabled(True)

    def open_resume_workspace(self):
        if self._current_opportunity_id is None:
            return

        self.open_resume_workspace_requested.emit(self._current_opportunity_id)

    def open_cover_letter_workspace(self):
        if self._current_opportunity_id is None:
            return

        self.open_cover_letter_workspace_requested.emit(self._current_opportunity_id)

    def _refresh_assessment_display(self, opportunity_id: int):
        assessment = self.controller.get_latest_assessment(opportunity_id)

        if assessment is None:
            self._hide_assessment_display()
            return

        self._show_assessment_display(assessment)

    def _hide_assessment_display(self):
        self.assessment_placeholder.setVisible(True)

        for widget in (
            self.assessment_score,
            self.assessment_sub_scores,
            self.assessment_recommendation,
            self.assessment_reasoning,
            self.assessment_generated_at,
        ):
            widget.setVisible(False)

    def _show_assessment_display(self, assessment):
        self.assessment_placeholder.setVisible(False)

        self.assessment_score.setText(f"Overall Score: {assessment.score}  |  Fit: {assessment.fit_score}")
        self.assessment_sub_scores.setText(
            f"Posting Age: {assessment.posting_age_score}  |  Company: {assessment.company_score}  |  "
            f"Remote: {assessment.remote_score}  |  Salary: {assessment.salary_score}  |  ATS: {assessment.ats_score}"
        )
        self.assessment_recommendation.setText(f"Recommendation: {assessment.recommendation}")
        self.assessment_reasoning.setPlainText(assessment.reasoning)
        self.assessment_generated_at.setText(
            f"Generated: {assessment.created_at.strftime('%Y-%m-%d %H:%M')}"
        )

        for widget in (
            self.assessment_score,
            self.assessment_sub_scores,
            self.assessment_recommendation,
            self.assessment_reasoning,
            self.assessment_generated_at,
        ):
            widget.setVisible(True)

    def save_status(self):
        if self._current_opportunity_id is None:
            return

        new_status = self.status_combo.currentText()
        updated = self.controller.update_opportunity_status(self._current_opportunity_id, new_status)

        self.refresh()
        self._reselect_opportunity(updated.id)
        self.status_save_result.setText(f"Status saved: {updated.status}")

    def _reselect_opportunity(self, opportunity_id: int):
        for index in range(self.opportunities_list.count()):
            item = self.opportunities_list.item(index)
            opportunity, _job = item.data(Qt.ItemDataRole.UserRole)

            if opportunity.id == opportunity_id:
                item.setSelected(True)
                self.opportunities_list.setCurrentItem(item)
                break

    def _show_status_editor(self, opportunity):
        self._current_opportunity_id = opportunity.id

        index = self.status_combo.findText(opportunity.status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

        self.status_combo.setVisible(True)
        self.save_status_button.setVisible(True)

    def _hide_status_editor(self):
        self._current_opportunity_id = None
        self.status_combo.setVisible(False)
        self.save_status_button.setVisible(False)

    def _list_item_text(self, opportunity, job) -> str:
        if job is None:
            return f"(Job unavailable) ({opportunity.status})"

        return f"{job.title} — {job.company} ({opportunity.status})"

    def _show_placeholder(self, message: str = "Select an Opportunity to see details."):
        self.details_placeholder.setText(message)
        self.details_placeholder.setVisible(True)

        for widget in (
            self.detail_job_title,
            self.detail_company,
            self.detail_location,
            self.detail_source,
            self.detail_status,
            self.detail_dates,
            self.detail_description,
        ):
            widget.setVisible(False)

    def _show_details(self, opportunity, job):
        self.details_placeholder.setVisible(False)

        self.detail_job_title.setText(f"Title: {job.title}")
        self.detail_company.setText(f"Company: {job.company}")
        self.detail_location.setText(f"Location: {job.location or 'Not specified'}")
        self.detail_source.setText(f"Source: {job.source or 'Unknown'}")
        self.detail_status.setText(f"Status: {opportunity.status}")
        self.detail_dates.setText(
            f"Created: {opportunity.created_at.strftime('%Y-%m-%d %H:%M')}  |  "
            f"Updated: {opportunity.updated_at.strftime('%Y-%m-%d %H:%M')}"
        )
        self.detail_description.setPlainText(job.description or "No description available.")

        for widget in (
            self.detail_job_title,
            self.detail_company,
            self.detail_location,
            self.detail_source,
            self.detail_status,
            self.detail_dates,
            self.detail_description,
        ):
            widget.setVisible(True)
