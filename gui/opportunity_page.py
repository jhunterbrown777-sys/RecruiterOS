from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
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

        panel_layout.addWidget(panel_title)
        panel_layout.addWidget(self.opportunities_list)

        panel.setLayout(panel_layout)
        root.addWidget(panel)

        self.setLayout(root)
        self.refresh()

    def refresh(self):
        self.opportunities_list.clear()

        for opportunity, job in self.controller.get_opportunities():
            if job is None:
                continue

            self.opportunities_list.addItem(
                f"{job.title} — {job.company} ({opportunity.status})"
            )
