from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFrame,
)


class ApplicationPackagePage(QWidget):
    """Read-only view composing everything behind one Application.

    Nothing here is editable -- edits happen in the Opportunity, Resume,
    Cover Letter, or Application workspace this data comes from.
    """

    back_requested = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        root = QVBoxLayout()

        header = QLabel("Application Package")
        header.setObjectName("PageTitle")

        subtitle = QLabel("Read-only snapshot of everything behind this Application")
        subtitle.setObjectName("PageSubtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        back_button = QPushButton("Back to Applications")
        back_button.clicked.connect(self.back_requested.emit)
        root.addWidget(back_button)

        self.placeholder = QLabel("No Application selected.")
        self.placeholder.setObjectName("PageSubtitle")
        root.addWidget(self.placeholder)

        root.addWidget(self._panel("Opportunity", "opportunity_summary"))
        root.addWidget(self._panel("Assessment", "assessment_summary", text_edit=True))
        root.addWidget(self._panel("Application Status", "application_summary"))
        root.addWidget(self._panel("Resume", "resume_summary", text_edit=True))
        root.addWidget(self._panel("Cover Letter", "cover_letter_summary", text_edit=True))
        root.addWidget(self._panel("Supporting Documents", "documents_summary", text_edit=True))

        self._panels = [
            self.opportunity_summary_panel,
            self.assessment_summary_panel,
            self.application_summary_panel,
            self.resume_summary_panel,
            self.cover_letter_summary_panel,
            self.documents_summary_panel,
        ]

        self._current_application_id = None

        self.setLayout(root)
        self._show_placeholder()

    def _panel(self, title: str, field_name: str, text_edit: bool = False) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        layout.addWidget(title_label)

        if text_edit:
            widget = QTextEdit()
            widget.setReadOnly(True)
        else:
            widget = QLabel("")

        layout.addWidget(widget)
        panel.setLayout(layout)

        setattr(self, f"{field_name}", widget)
        setattr(self, f"{field_name}_panel", panel)

        return panel

    def load(self, application_id: int):
        self._current_application_id = application_id
        package = self.controller.get_application_package(application_id)

        self.placeholder.setVisible(False)
        for panel in self._panels:
            panel.setVisible(True)

        application = package["application"]
        opportunity = package["opportunity"]
        job = package["job"]
        assessment = package["assessment"]
        resume = package["resume"]
        cover_letter = package["cover_letter"]
        documents = package["documents"]

        if job is not None:
            self.opportunity_summary.setText(
                f"{job.title} — {job.company}\n"
                f"Location: {job.location or 'Not specified'}\n"
                f"Opportunity Status: {opportunity.status if opportunity else 'Unknown'}"
            )
        else:
            self.opportunity_summary.setText("Job details unavailable for this Opportunity.")

        if assessment is not None:
            self.assessment_summary.setPlainText(
                f"Score: {assessment.score}  |  Fit: {assessment.fit_score}\n"
                f"Recommendation: {assessment.recommendation}\n\n"
                f"{assessment.reasoning}"
            )
        else:
            self.assessment_summary.setPlainText("No Assessment on record for this Opportunity.")

        applied_at = application.applied_at.strftime("%Y-%m-%d %H:%M") if application.applied_at else "Not yet"
        self.application_summary.setText(
            f"Status: {application.status}\n"
            f"Applied At: {applied_at}\n"
            f"Notes: {application.notes or '(none)'}"
        )

        if resume is not None:
            self.resume_summary.setPlainText(f"{resume.title} (v{resume.version})\n\n{resume.content}")
        else:
            self.resume_summary.setPlainText("No Resume linked to this Application.")

        if cover_letter is not None:
            self.cover_letter_summary.setPlainText(
                f"{cover_letter.title} (v{cover_letter.version})\n\n{cover_letter.content}"
            )
        else:
            self.cover_letter_summary.setPlainText("No Cover Letter linked to this Application.")

        if documents:
            lines = [f"{document.title} — {document.document_type} (v{document.version})" for document in documents]
            self.documents_summary.setPlainText("\n".join(lines))
        else:
            self.documents_summary.setPlainText("No supporting Documents in the library yet.")

    def _show_placeholder(self):
        self.placeholder.setVisible(True)
        for panel in self._panels:
            panel.setVisible(False)
