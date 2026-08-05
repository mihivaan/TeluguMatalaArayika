"""
తెలుగు మాటల అరయిక (TLRE)

Research Question Editor Dialog

Version: 0.2.0
Reference Point: RP-006

Dialog for creating and editing Research Questions.
"""

from __future__ import annotations

import sqlite3
import sys

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from src.constants import RESEARCH_QUESTION_STATUSES
from src.models import ResearchQuestion
from src.queries import (
    create_research_question,
    get_research_questions_for_entry,
    update_research_question,
)


class QuestionEditorDialog(QDialog):
    """
    Dialog for creating and editing ResearchQuestion records.
    """

    def __init__(
        self,
        entry_id: int,
        question: ResearchQuestion | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.entry_id = entry_id
        self.question = question

        self.setModal(True)

        if self.question is None:
            self.setWindowTitle("Add Research Question")
        else:
            self.setWindowTitle("Edit Research Question")

        self.resize(550, 380)

        self.init_ui()

        if self.question is not None:
            self.populate_fields()

    def init_ui(self) -> None:
        """
        Construct the dialog user interface.
        """

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.question_text_input = QLineEdit()
        self.question_text_input.setPlaceholderText(
            "Enter research question statement..."
        )

        self.parent_question_combo = QComboBox()

        # Root question option
        self.parent_question_combo.addItem(
            "<Root Question>",
            None,
        )

        for rq in get_research_questions_for_entry(self.entry_id):

            # Prevent self-parenting during edit mode
            if (
                self.question is not None
                and rq.id == self.question.id
            ):
                continue

            display_text = (
                f"{rq.id}: {rq.question_text}"
            )

            self.parent_question_combo.addItem(
                display_text,
                rq.id,
            )

        self.status_combo = QComboBox()
        self.status_combo.addItems(
            RESEARCH_QUESTION_STATUSES
        )

        self.resolution_summary_input = QLineEdit()
        self.resolution_summary_input.setPlaceholderText(
            "Optional resolution summary..."
        )

        form_layout.addRow(
            "Question:",
            self.question_text_input,
        )

        form_layout.addRow(
            "Parent Question:",
            self.parent_question_combo,
        )

        form_layout.addRow(
            "Status:",
            self.status_combo,
        )

        form_layout.addRow(
            "Resolution Summary:",
            self.resolution_summary_input,
        )

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save
            | QDialogButtonBox.Cancel
        )

        self.button_box.accepted.connect(
            self.on_save
        )

        self.button_box.rejected.connect(
            self.reject
        )

        layout.addWidget(self.button_box)

    def populate_fields(self) -> None:
        """
        Populate widgets from an existing ResearchQuestion.
        """

        assert self.question is not None

        self.question_text_input.setText(
            self.question.question_text
        )

        parent_index = (
            self.parent_question_combo.findData(
                self.question.parent_question_id
            )
        )

        if parent_index >= 0:
            self.parent_question_combo.setCurrentIndex(
                parent_index
            )

        status_index = self.status_combo.findText(
            self.question.status
        )

        if status_index >= 0:
            self.status_combo.setCurrentIndex(
                status_index
            )

        self.resolution_summary_input.setText(
            self.question.resolution_summary or ""
        )

    def on_save(self) -> None:
        """
        Validate and save the Research Question.
        """

        question_text = (
            self.question_text_input.text().strip()
        )

        if not question_text:
            QMessageBox.critical(
                self,
                "Validation Error",
                "Research question cannot be empty.",
            )
            return

        resolution_summary = (
            self.resolution_summary_input.text().strip()
        )

        if resolution_summary == "":
            resolution_summary = None

        parent_question_id = (
            self.parent_question_combo.currentData()
        )

        try:

            if self.question is None:

                new_question = ResearchQuestion(
                    entry_id=self.entry_id,
                    parent_question_id=parent_question_id,
                    question_text=question_text,
                    status=self.status_combo.currentText(),
                    resolution_summary=resolution_summary,
                )

                create_research_question(
                    new_question
                )

            else:

                self.question.entry_id = self.entry_id

                self.question.parent_question_id = (
                    parent_question_id
                )

                self.question.question_text = (
                    question_text
                )

                self.question.status = (
                    self.status_combo.currentText()
                )

                self.question.resolution_summary = (
                    resolution_summary
                )

                update_research_question(
                    self.question
                )

        except (sqlite3.Error, ValueError) as exc:

            QMessageBox.critical(
                self,
                "Database Error",
                str(exc),
            )

            return

        self.accept()


def main() -> None:
    """
    Standalone dialog runner.
    """

    app = QApplication(sys.argv)

    dialog = QuestionEditorDialog(
        entry_id=1,
    )

    dialog.exec()

    sys.exit(0)


if __name__ == "__main__":
    main()