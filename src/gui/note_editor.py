"""
తెలుగు మాటల అరయిక (TLRE)

Research Journal Note Editor

Version: 0.2.0
Reference Point: RP-006

Dialog for recording timestamped research journal notes.
Research notes are append-only and therefore support
Create Mode only.
"""

from __future__ import annotations

import sqlite3
import sys

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

from src.models import ResearchNote
from src.queries import add_research_note


class NoteEditorDialog(QDialog):
    """
    Dialog for adding timestamped research journal notes.
    """

    def __init__(
        self,
        entry_id: int,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.entry_id = entry_id

        self.setModal(True)
        self.setWindowTitle(
            "Add Journal Progress Note"
        )
        self.resize(500, 300)

        self.init_ui()

    def init_ui(self) -> None:
        """
        Construct the dialog user interface.
        """

        layout = QVBoxLayout(self)

        header_label = QLabel(
            "Record research progress, field observations, or "
            "literature findings for this entry:"
        )

        header_label.setWordWrap(True)

        layout.addWidget(header_label)

        self.note_text_input = QTextEdit()

        self.note_text_input.setPlaceholderText(
            "Type research progress note here..."
        )

        layout.addWidget(self.note_text_input)

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

    def on_save(self) -> None:
        """
        Validate and save the research journal note.
        """

        text = (
            self.note_text_input
            .toPlainText()
            .strip()
        )

        if not text:
            QMessageBox.critical(
                self,
                "Validation Error",
                "Research note cannot be empty.",
            )
            return

        note = ResearchNote(
            entry_id=self.entry_id,
            note_text=text,
        )

        try:

            add_research_note(note)

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

    dialog = NoteEditorDialog(
        entry_id=1,
    )

    dialog.exec()

    sys.exit(0)


if __name__ == "__main__":
    main()