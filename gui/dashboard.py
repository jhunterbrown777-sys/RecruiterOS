from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QListWidget,
)


class StatCard(QFrame):
    def __init__(self, title: str, value: str):
        super().__init__()

        self.setObjectName("StatCard")

        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setObjectName("StatTitle")

        value_label = QLabel(value)
        value_label.setObjectName("StatValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        self.setLayout(layout)


class DashboardPage(QWidget):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        layout = QVBoxLayout()

        header = QLabel("Dashboard")
        header.setObjectName("PageTitle")

        subtitle = QLabel("Overview of your job search and application pipeline")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(header)
        layout.addWidget(subtitle)

        stats = self.controller.get_dashboard_stats()

        stats_row = QHBoxLayout()
        stats_row.addWidget(StatCard("Jobs Discovered", str(stats["jobs_discovered"])))
        stats_row.addWidget(StatCard("Qualified", str(stats["qualified_opportunities"])))
        stats_row.addWidget(StatCard("Applications", str(stats["applications_sent"])))
        stats_row.addWidget(StatCard("Interviews", str(stats["interviews"])))
        stats_row.addWidget(StatCard("Offers", str(stats["offers"])))

        layout.addLayout(stats_row)

        jobs_label = QLabel("Recent Jobs")
        jobs_label.setObjectName("SectionTitle")
        layout.addWidget(jobs_label)

        self.jobs_list = QListWidget()

        for job in self.controller.get_recent_jobs():
            title = job[1]
            company = job[2]
            source = job[6]
            self.jobs_list.addItem(f"{title} — {company} ({source})")

        layout.addWidget(self.jobs_list)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)

        layout.addWidget(refresh_button)

        self.setLayout(layout)

    def refresh(self):
        self.jobs_list.clear()

        for job in self.controller.get_recent_jobs():
            title = job[1]
            company = job[2]
            source = job[6]
            self.jobs_list.addItem(f"{title} — {company} ({source})")