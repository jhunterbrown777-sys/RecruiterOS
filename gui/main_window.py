from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
)

from gui.controller import AppController
from gui.dashboard import DashboardPage
from gui.opportunity_page import OpportunityPage
from gui.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RecruiterOS — Mission Control")
        self.resize(1350, 820)

        self.controller = AppController()

        root = QWidget()
        root_layout = QHBoxLayout()

        sidebar_widget = self.build_sidebar()

        self.dashboard = DashboardPage(self.controller)
        self.settings_page = SettingsPage(self.controller)
        self.opportunity_page = OpportunityPage(self.controller)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.opportunity_page)

        root_layout.addWidget(sidebar_widget)
        root_layout.addWidget(self.pages)

        root.setLayout(root_layout)
        self.setCentralWidget(root)

        self.settings_button.clicked.connect(self.show_settings)
        self.opportunities_button.clicked.connect(self.show_opportunities)

        self.apply_styles()

    def show_settings(self):
        self.settings_page.refresh()
        self.pages.setCurrentWidget(self.settings_page)

    def show_opportunities(self):
        self.opportunity_page.refresh()
        self.pages.setCurrentWidget(self.opportunity_page)

    def build_sidebar(self):
        sidebar = QVBoxLayout()

        logo = QLabel("RecruiterOS")
        logo.setObjectName("Logo")

        subtitle = QLabel("Mission Control")
        subtitle.setObjectName("SidebarSubtitle")

        sidebar.addWidget(logo)
        sidebar.addWidget(subtitle)

        buttons = [
            "Mission Control",
            "Discover",
            "Opportunities",
            "Companies",
            "Documents",
            "CRM",
            "Analytics",
        ]

        for label in buttons:
            button = QPushButton(label)
            button.setObjectName("SidebarButton")
            sidebar.addWidget(button)

            if label == "Opportunities":
                self.opportunities_button = button

        sidebar.addStretch()

        self.settings_button = QPushButton("Settings")
        self.settings_button.setObjectName("SidebarButton")
        sidebar.addWidget(self.settings_button)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("Sidebar")
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(240)

        return sidebar_widget

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b1120;
            }

            QWidget {
                background-color: #0b1120;
                color: #e5e7eb;
                font-family: Segoe UI;
                font-size: 14px;
            }

            #Sidebar {
                background-color: #0f172a;
                border-right: 1px solid #1e293b;
            }

            #Logo {
                font-size: 25px;
                font-weight: bold;
                color: #38bdf8;
                padding: 22px 20px 0px 20px;
            }

            #SidebarSubtitle {
                color: #94a3b8;
                padding: 0px 20px 18px 20px;
            }

            #SidebarButton {
                background-color: transparent;
                color: #cbd5e1;
                text-align: left;
                padding: 12px 16px;
                margin: 2px 10px;
                border: none;
                border-radius: 10px;
            }

            #SidebarButton:hover {
                background-color: #1e293b;
                color: #f8fafc;
            }

            #PageTitle {
                font-size: 32px;
                font-weight: bold;
                color: #f8fafc;
                margin-top: 12px;
            }

            #PageSubtitle {
                color: #94a3b8;
                margin-bottom: 18px;
            }

            #SectionTitle {
                font-size: 17px;
                font-weight: bold;
                color: #f8fafc;
                margin-bottom: 8px;
            }

            #StatCard {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 14px;
                padding: 18px;
                min-height: 105px;
            }

            #StatTitle {
                color: #94a3b8;
                font-size: 13px;
            }

            #StatValue {
                color: #22c55e;
                font-size: 31px;
                font-weight: bold;
            }

            #Panel {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 14px;
                padding: 12px;
            }

            QListWidget {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 10px;
                padding: 8px;
                color: #e5e7eb;
            }

            QListWidget::item {
                padding: 7px;
            }

            QListWidget::item:hover {
                background-color: #1f2937;
                border-radius: 6px;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 10px;
                border-radius: 8px;
                border: none;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)