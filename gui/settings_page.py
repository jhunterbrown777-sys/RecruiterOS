from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFrame,
)


class SettingsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        root = QVBoxLayout()

        header = QLabel("Settings")
        header.setObjectName("PageTitle")

        subtitle = QLabel("Candidate profile")
        subtitle.setObjectName("PageSubtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout()

        name_label = QLabel("Name")
        name_label.setObjectName("SectionTitle")
        self.name_input = QLineEdit()

        profile_label = QLabel("Candidate Profile")
        profile_label.setObjectName("SectionTitle")
        self.profile_input = QTextEdit()

        panel_layout.addWidget(name_label)
        panel_layout.addWidget(self.name_input)
        panel_layout.addWidget(profile_label)
        panel_layout.addWidget(self.profile_input)

        panel.setLayout(panel_layout)
        root.addWidget(panel)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save)
        root.addWidget(save_button)

        self.setLayout(root)
        self.refresh()

    def refresh(self):
        candidate = self.controller.get_candidate()
        self.name_input.setText(candidate.name)
        self.profile_input.setPlainText(candidate.candidate_profile)

    def save(self):
        self.controller.update_candidate(
            self.name_input.text(),
            self.profile_input.toPlainText(),
        )
