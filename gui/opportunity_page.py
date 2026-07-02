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


class OpportunityPage(QWidget):
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
        selected = self.opportunities_list.selectedItems()

        if not selected:
            self._show_placeholder()
            return

        opportunity, job = selected[0].data(Qt.ItemDataRole.UserRole)

        if job is None:
            self._show_placeholder("Job details unavailable for this Opportunity.")
            return

        self._show_details(opportunity, job)

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
