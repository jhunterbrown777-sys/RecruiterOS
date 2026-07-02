from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
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

        placeholder_panel = QFrame()
        placeholder_panel.setObjectName("Panel")
        placeholder_layout = QVBoxLayout()

        placeholder_label = QLabel("Resume Workspace coming soon.")
        placeholder_label.setObjectName("PageSubtitle")
        placeholder_layout.addWidget(placeholder_label)

        placeholder_panel.setLayout(placeholder_layout)
        root.addWidget(placeholder_panel)

        self.setLayout(root)
        self.refresh()

    def refresh(self):
        pass
