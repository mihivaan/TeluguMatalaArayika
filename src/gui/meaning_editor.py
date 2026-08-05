"""
తెలుగు మాటల అరయిక (TLRE)

Meaning Editor Dialog

Version: 0.2.0
Reference Point: RP-006

Dialog for creating and editing lexical meanings.
"""

from __future__ import annotations

import sqlite3
import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from src.models import Meaning
from src.queries import (
    create_meaning,
    update_meaning,
)


class MeaningEditorDialog(QDialog):
    """
    Dialog for creating and editing Meaning records.
    """

    def __init__(
        self,
        entry_id: int,
        meaning: Meaning | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.entry_id = entry_id
        self.meaning = meaning

        self.setModal(True)

        if self.meaning is None:
            self.setWindowTitle("Add Meaning")
        else:
            self.setWindowTitle("Edit Meaning")

        self.resize(450, 220)

        self.init_ui()

        if self.meaning is not None:
            self.populate_fields()

    def init_ui(self) -> None:
        """
        Construct the dialog UI.
        """

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.meaning_order_input = QSpinBox()
        self.meaning_order_input.setMinimum(1)
        self.meaning_order_input.setValue(1)

        self.meaning_input = QLineEdit()
        self.meaning_input.setPlaceholderText(
            "Enter meaning..."
        )

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText(
            "Optional notes..."
        )

        form_layout.addRow(
            "Meaning Order:",
            self.meaning_order_input,
        )
        form_layout.addRow(
            "Meaning:",
            self.meaning_input,
        )
        form_layout.addRow(
            "Notes:",
            self.notes_input,
        )

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save
            | QDialogButtonBox.Cancel
        )

        self.button_box.accepted.connect(self.on_save)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

    def populate_fields(self) -> None:
        """
        Populate widgets from an existing Meaning.
        """

        assert self.meaning is not None

        self.meaning_order_input.setValue(
            self.meaning.meaning_order
        )

        self.meaning_input.setText(
            self.meaning.meaning
        )

        self.notes_input.setText(
            self.meaning.notes or ""
        )

    def on_save(self) -> None:
        """
        Validate and save the Meaning.
        """

        meaning_text = self.meaning_input.text().strip()

        if not meaning_text:
            QMessageBox.critical(
                self,
                "Validation Error",
                "Meaning cannot be empty.",
            )
            return

        notes = self.notes_input.text().strip()

        if notes == "":
            notes = None

        try:

            if self.meaning is None:

                new_meaning = Meaning(
                    entry_id=self.entry_id,
                    meaning_order=self.meaning_order_input.value(),
                    meaning=meaning_text,
                    notes=notes,
                )

                create_meaning(new_meaning)

            else:

                self.meaning.meaning_order = (
                    self.meaning_order_input.value()
                )

                self.meaning.meaning = meaning_text
                self.meaning.notes = notes

                update_meaning(self.meaning)

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

    dialog = MeaningEditorDialog(
        entry_id=1,
    )

    dialog.exec()

    sys.exit(0)


if __name__ == "__main__":
    main()