from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
)

from gui.controller import AppController
from gui.dashboard import DashboardPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RecruiterOS")
        self.resize(1200, 750)

        self.controller = AppController()

        root = QWidget()
        root_layout = QHBoxLayout()

        sidebar = QVBoxLayout()

        logo = QLabel("RecruiterOS")
        logo.setObjectName("Logo")

        dashboard_button = QPushButton("Dashboard")
        dashboard_button.setObjectName("SidebarButton")

        discover_button = QPushButton("Discover")
        discover_button.setObjectName("SidebarButton")

        jobs_button = QPushButton("Jobs")
        jobs_button.setObjectName("SidebarButton")

        companies_button = QPushButton("Companies")
        companies_button.setObjectName("SidebarButton")

        settings_button = QPushButton("Settings")
        settings_button.setObjectName("SidebarButton")

        sidebar.addWidget(logo)
        sidebar.addWidget(dashboard_button)
        sidebar.addWidget(discover_button)
        sidebar.addWidget(jobs_button)
        sidebar.addWidget(companies_button)
        sidebar.addStretch()
        sidebar.addWidget(settings_button)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("Sidebar")
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(220)

        self.dashboard = DashboardPage(self.controller)

        root_layout.addWidget(sidebar_widget)
        root_layout.addWidget(self.dashboard)

        root.setLayout(root_layout)
        self.setCentralWidget(root)

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }

            QWidget {
                background-color: #0f172a;
                color: #e5e7eb;
                font-family: Segoe UI;
                font-size: 14px;
            }

            #Sidebar {
                background-color: #111827;
                border-right: 1px solid #1f2937;
            }

            #Logo {
                font-size: 24px;
                font-weight: bold;
                color: #60a5fa;
                padding: 20px;
            }

            #SidebarButton {
                background-color: transparent;
                color: #d1d5db;
                text-align: left;
                padding: 12px;
                border: none;
                border-radius: 8px;
            }

            #SidebarButton:hover {
                background-color: #1f2937;
            }

            #PageTitle {
                font-size: 28px;
                font-weight: bold;
                color: #f9fafb;
            }

            #PageSubtitle {
                color: #9ca3af;
                margin-bottom: 20px;
            }

            #SectionTitle {
                font-size: 18px;
                font-weight: bold;
                margin-top: 20px;
            }

            #StatCard {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 12px;
                padding: 16px;
                min-height: 100px;
            }

            #StatTitle {
                color: #9ca3af;
                font-size: 13px;
            }

            #StatValue {
                color: #22c55e;
                font-size: 30px;
                font-weight: bold;
            }

            QListWidget {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 12px;
                padding: 8px;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 10px;
                border-radius: 8px;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)