from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QFrame,
)


class CoverLetterPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        root = QVBoxLayout()

        header = QLabel("Cover Letters")
        header.setObjectName("PageTitle")

        subtitle = QLabel("Manage AI-tailored cover letters for your Opportunities")
        subtitle.setObjectName("PageSubtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout()

        panel_title = QLabel("Cover Letters")
        panel_title.setObjectName("SectionTitle")

        self.cover_letter_list = QListWidget()
        self.cover_letter_list.itemSelectionChanged.connect(self.update_details)

        self.cover_letter_list_empty_state = QLabel(
            "No cover letters yet. Create one below or generate one from an Opportunity."
        )
        self.cover_letter_list_empty_state.setObjectName("PageSubtitle")

        panel_layout.addWidget(panel_title)
        panel_layout.addWidget(self.cover_letter_list)
        panel_layout.addWidget(self.cover_letter_list_empty_state)

        panel.setLayout(panel_layout)
        root.addWidget(panel)

        root.addWidget(self.build_details_panel())
        root.addWidget(self.build_generate_panel())
        root.addWidget(self.build_create_panel())

        self._current_cover_letter_id = None

        self.setLayout(root)
        self.refresh()

    def build_details_panel(self) -> QFrame:
        details_panel = QFrame()
        details_panel.setObjectName("Panel")
        details_layout = QVBoxLayout()

        details_title = QLabel("Details")
        details_title.setObjectName("SectionTitle")
        details_layout.addWidget(details_title)

        self.details_placeholder = QLabel("Select a Cover Letter to see details.")
        self.details_placeholder.setObjectName("PageSubtitle")
        details_layout.addWidget(self.details_placeholder)

        self.detail_title = QLabel("")
        self.detail_version = QLabel("")
        self.detail_dates = QLabel("")

        for label in (self.detail_title, self.detail_version, self.detail_dates):
            details_layout.addWidget(label)

        self.detail_content = QTextEdit()
        details_layout.addWidget(self.detail_content)

        self.save_content_button = QPushButton("Save Changes")
        self.save_content_button.clicked.connect(self.save_cover_letter_content)
        details_layout.addWidget(self.save_content_button)

        self.duplicate_button = QPushButton("Duplicate as New Version")
        self.duplicate_button.clicked.connect(self.duplicate_cover_letter)
        details_layout.addWidget(self.duplicate_button)

        self.edit_result = QLabel("")
        self.edit_result.setObjectName("PageSubtitle")
        details_layout.addWidget(self.edit_result)

        details_panel.setLayout(details_layout)
        return details_panel

    def build_generate_panel(self) -> QFrame:
        generate_panel = QFrame()
        generate_panel.setObjectName("Panel")
        generate_layout = QVBoxLayout()

        generate_title = QLabel("Generate Tailored Cover Letter")
        generate_title.setObjectName("SectionTitle")
        generate_layout.addWidget(generate_title)

        self.opportunity_combo = QComboBox()
        generate_layout.addWidget(self.opportunity_combo)

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate_cover_letter)
        generate_layout.addWidget(self.generate_button)

        self.generate_empty_state = QLabel("No Opportunities with a resolvable Job are available yet.")
        self.generate_empty_state.setObjectName("PageSubtitle")
        generate_layout.addWidget(self.generate_empty_state)

        self.generate_result = QLabel("")
        self.generate_result.setObjectName("PageSubtitle")
        generate_layout.addWidget(self.generate_result)

        generate_panel.setLayout(generate_layout)
        return generate_panel

    def build_create_panel(self) -> QFrame:
        create_panel = QFrame()
        create_panel.setObjectName("Panel")
        create_layout = QVBoxLayout()

        create_title = QLabel("Create Cover Letter")
        create_title.setObjectName("SectionTitle")
        create_layout.addWidget(create_title)

        title_label = QLabel("Title")
        create_layout.addWidget(title_label)

        self.new_title_input = QLineEdit()
        self.new_title_input.textChanged.connect(self._update_create_button_state)
        create_layout.addWidget(self.new_title_input)

        content_label = QLabel("Content")
        create_layout.addWidget(content_label)

        self.new_content_input = QTextEdit()
        create_layout.addWidget(self.new_content_input)

        self.create_save_button = QPushButton("Save")
        self.create_save_button.setEnabled(False)
        self.create_save_button.clicked.connect(self.create_cover_letter)
        create_layout.addWidget(self.create_save_button)

        self.create_result = QLabel("")
        self.create_result.setObjectName("PageSubtitle")
        create_layout.addWidget(self.create_result)

        create_panel.setLayout(create_layout)
        return create_panel

    def refresh(self):
        self.create_result.setText("")
        self.generate_result.setText("")
        self.cover_letter_list.clear()

        for cover_letter in self.controller.get_cover_letters():
            item = QListWidgetItem(self._list_item_text(cover_letter))
            item.setData(Qt.ItemDataRole.UserRole, cover_letter)
            self.cover_letter_list.addItem(item)

        self.cover_letter_list_empty_state.setVisible(self.cover_letter_list.count() == 0)

        self._refresh_opportunity_combo()
        self.update_details()

    def _refresh_opportunity_combo(self):
        self.opportunity_combo.clear()

        for opportunity, job in self.controller.get_opportunities():
            if job is None:
                continue

            self.opportunity_combo.addItem(f"{job.title} — {job.company}", opportunity.id)

        has_opportunities = self.opportunity_combo.count() > 0
        self.opportunity_combo.setVisible(has_opportunities)
        self.generate_button.setEnabled(has_opportunities)
        self.generate_empty_state.setVisible(not has_opportunities)

    def _update_create_button_state(self):
        self.create_save_button.setEnabled(bool(self.new_title_input.text().strip()))

    def select_opportunity(self, opportunity_id: int):
        """Best-effort preselect an Opportunity in the generate combo."""
        index = self.opportunity_combo.findData(opportunity_id)

        if index >= 0:
            self.opportunity_combo.setCurrentIndex(index)

    def generate_cover_letter(self):
        opportunity_id = self.opportunity_combo.currentData()

        if opportunity_id is None:
            return

        self.generate_button.setEnabled(False)
        self.generate_result.setText("Generating…")
        QApplication.processEvents()

        try:
            cover_letter = self.controller.generate_cover_letter_for_opportunity(opportunity_id)
            self.refresh()
            self._select_cover_letter(cover_letter.id)
            self.generate_result.setText(f"Generated: {cover_letter.title}")
        except Exception as error:
            self.generate_result.setText(f"Generation failed: {error}")
        finally:
            self.generate_button.setEnabled(self.opportunity_combo.count() > 0)

    def create_cover_letter(self):
        title = self.new_title_input.text().strip()

        if not title:
            self.create_result.setText("Title is required.")
            return

        content = self.new_content_input.toPlainText()
        cover_letter = self.controller.create_cover_letter(title, content)

        self.new_title_input.clear()
        self.new_content_input.clear()

        self.refresh()
        self._select_cover_letter(cover_letter.id)
        self.create_result.setText(f"Created: {cover_letter.title}")

    def select_cover_letter(self, cover_letter_id: int):
        """Public entry point for other pages to preselect a Cover Letter here."""
        self._select_cover_letter(cover_letter_id)

    def _select_cover_letter(self, cover_letter_id: int):
        for index in range(self.cover_letter_list.count()):
            item = self.cover_letter_list.item(index)
            cover_letter = item.data(Qt.ItemDataRole.UserRole)

            if cover_letter.id == cover_letter_id:
                item.setSelected(True)
                self.cover_letter_list.setCurrentItem(item)
                break

    def update_details(self):
        self.edit_result.setText("")
        selected = self.cover_letter_list.selectedItems()

        if not selected:
            if self.cover_letter_list.count() == 0:
                self._show_placeholder("No cover letters to select yet.")
            else:
                self._show_placeholder()
            return

        cover_letter = selected[0].data(Qt.ItemDataRole.UserRole)
        self._show_details(cover_letter)

    def save_cover_letter_content(self):
        if self._current_cover_letter_id is None:
            return

        content = self.detail_content.toPlainText()
        updated = self.controller.update_cover_letter_content(self._current_cover_letter_id, content)

        self.refresh()
        self._select_cover_letter(updated.id)
        self.edit_result.setText(f"Saved: {updated.title}")

    def duplicate_cover_letter(self):
        if self._current_cover_letter_id is None:
            return

        new_cover_letter = self.controller.duplicate_cover_letter(self._current_cover_letter_id)

        self.refresh()
        self._select_cover_letter(new_cover_letter.id)
        self.edit_result.setText(f"Duplicated as version {new_cover_letter.version}: {new_cover_letter.title}")

    def _list_item_text(self, cover_letter) -> str:
        return f"{cover_letter.title} (v{cover_letter.version})"

    def _show_placeholder(self, message: str = "Select a Cover Letter to see details."):
        self._current_cover_letter_id = None
        self.details_placeholder.setText(message)
        self.details_placeholder.setVisible(True)

        for widget in (
            self.detail_title,
            self.detail_version,
            self.detail_dates,
            self.detail_content,
            self.save_content_button,
            self.duplicate_button,
        ):
            widget.setVisible(False)

    def _show_details(self, cover_letter):
        self._current_cover_letter_id = cover_letter.id
        self.details_placeholder.setVisible(False)

        self.detail_title.setText(f"Title: {cover_letter.title}")
        self.detail_version.setText(f"Version: {cover_letter.version}")
        self.detail_dates.setText(
            f"Created: {cover_letter.created_at.strftime('%Y-%m-%d %H:%M')}  |  "
            f"Updated: {cover_letter.updated_at.strftime('%Y-%m-%d %H:%M')}"
        )
        self.detail_content.setPlainText(cover_letter.content or "")

        for widget in (
            self.detail_title,
            self.detail_version,
            self.detail_dates,
            self.detail_content,
            self.save_content_button,
            self.duplicate_button,
        ):
            widget.setVisible(True)
