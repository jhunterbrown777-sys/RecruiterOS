from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QGridLayout,
)


class StatCard(QFrame):
    def __init__(self, title: str, value: str, accent: str = "green"):
        super().__init__()
        self.setObjectName("StatCard")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("StatValue")

        title_label = QLabel(title)
        title_label.setObjectName("StatTitle")

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)

    def set_value(self, value: str):
        self.value_label.setText(value)


class MissionControlPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        root = QVBoxLayout()

        header = QLabel("Mission Control")
        header.setObjectName("PageTitle")

        subtitle = QLabel("Your AI recruiting command center")
        subtitle.setObjectName("PageSubtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        stats = self.controller.get_dashboard_stats()

        stats_row = QHBoxLayout()
        self.jobs_card = StatCard("Jobs Discovered", str(stats["jobs_discovered"]))
        self.qualified_card = StatCard("Qualified", str(stats["qualified_opportunities"]))
        self.applications_card = StatCard("Applications", str(stats["applications_sent"]))
        self.interviews_card = StatCard("Interviews", str(stats["interviews"]))
        self.offers_card = StatCard("Offers", str(stats["offers"]))

        stats_row.addWidget(self.jobs_card)
        stats_row.addWidget(self.qualified_card)
        stats_row.addWidget(self.applications_card)
        stats_row.addWidget(self.interviews_card)
        stats_row.addWidget(self.offers_card)

        root.addLayout(stats_row)

        main_grid = QGridLayout()

        self.opportunities_list = QListWidget()
        self.recent_jobs_list = QListWidget()
        self.activity_list = QListWidget()
        self.mission_list = QListWidget()
        self.queue_list = QListWidget()

        main_grid.addWidget(self.panel("Top Opportunities", self.opportunities_list), 0, 0)
        main_grid.addWidget(self.panel("Today's Mission", self.mission_list), 0, 1)
        main_grid.addWidget(self.build_recent_jobs_panel(), 1, 0)
        main_grid.addWidget(self.panel("AI Activity", self.activity_list), 1, 1)
        main_grid.addWidget(self.panel("Ready Queue", self.queue_list), 2, 0, 1, 2)

        root.addLayout(main_grid)

        button_row = QHBoxLayout()

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)

        discover_button = QPushButton("Discover Jobs")
        discover_button.clicked.connect(self.discover_jobs)

        button_row.addWidget(refresh_button)
        button_row.addWidget(discover_button)

        root.addLayout(button_row)

        self.setLayout(root)
        self.refresh()

    def build_recent_jobs_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Panel")

        layout = QVBoxLayout()

        label = QLabel("Recent Jobs")
        label.setObjectName("SectionTitle")

        layout.addWidget(label)
        layout.addWidget(self.recent_jobs_list)

        self.create_opportunity_button = QPushButton("Create Opportunity")
        self.create_opportunity_button.setEnabled(False)
        self.create_opportunity_button.clicked.connect(self.create_opportunity)
        layout.addWidget(self.create_opportunity_button)

        self.create_opportunity_status = QLabel("")
        self.create_opportunity_status.setObjectName("PageSubtitle")
        layout.addWidget(self.create_opportunity_status)

        frame.setLayout(layout)

        self.recent_jobs_list.itemSelectionChanged.connect(self.update_create_opportunity_button)

        return frame

    def update_create_opportunity_button(self):
        self.create_opportunity_button.setEnabled(bool(self.recent_jobs_list.selectedItems()))

    def create_opportunity(self):
        selected = self.recent_jobs_list.selectedItems()

        if not selected:
            return

        job = selected[0].data(Qt.ItemDataRole.UserRole)
        created = self.controller.create_opportunity_for_job(job.id)

        if created:
            self.create_opportunity_status.setText(f"Added to Opportunities: {job.title} — {job.company}")
        else:
            self.create_opportunity_status.setText(f"Already tracked: {job.title} — {job.company}")

    def panel(self, title: str, widget: QWidget) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Panel")

        layout = QVBoxLayout()

        label = QLabel(title)
        label.setObjectName("SectionTitle")

        layout.addWidget(label)
        layout.addWidget(widget)

        frame.setLayout(layout)
        return frame

    def refresh(self):
        stats = self.controller.get_dashboard_stats()

        self.jobs_card.set_value(str(stats["jobs_discovered"]))
        self.qualified_card.set_value(str(stats["qualified_opportunities"]))
        self.applications_card.set_value(str(stats["applications_sent"]))
        self.interviews_card.set_value(str(stats["interviews"]))
        self.offers_card.set_value(str(stats["offers"]))

        self.opportunities_list.clear()
        for job in self.controller.get_top_opportunities():
            self.opportunities_list.addItem(f"★ {job.title} — {job.company} ({job.source})")

        self.recent_jobs_list.clear()
        for job in self.controller.get_recent_jobs():
            item = QListWidgetItem(f"{job.title} — {job.company} ({job.source})")
            item.setData(Qt.ItemDataRole.UserRole, job)
            self.recent_jobs_list.addItem(item)

        self.create_opportunity_status.setText("")
        self.update_create_opportunity_button()

        self.activity_list.clear()
        for item in self.controller.get_activity_feed():
            self.activity_list.addItem(f"✓ {item}")

        self.mission_list.clear()
        for label, complete in self.controller.get_mission_items():
            icon = "✓" if complete else "○"
            self.mission_list.addItem(f"{icon} {label}")

        self.queue_list.clear()
        self.queue_list.addItem(f"Applications ready for review: {stats['ready_queue']}")
        self.queue_list.addItem(f"Average ATS Score: {stats['average_ats']}")

    def discover_jobs(self):
        self.controller.run_discovery()
        self.refresh()


DashboardPage = MissionControlPage