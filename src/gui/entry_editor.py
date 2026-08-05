"""
తెలుగు మాటల అరయిక (TLRE)

Entry Editor Dialog

Version: 0.2.0
Reference Point: RP-006

Dialog for creating and editing Entry records in the
Schema v2 lexical model.
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
    QSpinBox,
    QVBoxLayout,
)

from src.constants import CLASSIFICATION, PROVENANCE
from src.models import Entry
from src.queries import create_entry, update_entry


class EntryEditorDialog(QDialog):
    """
    Dialog for creating or editing an Entry.
    """

    def __init__(self, entry: Entry | None = None, parent=None) -> None:
        super().__init__(parent)

        self.entry = entry

        if self.entry is None:
            self.setWindowTitle("Create New Entry")
        else:
            self.setWindowTitle(f"Edit Entry (ID: {self.entry.id})")

        self.resize(500, 400)
        self.setModal(True)

        self.init_ui()
        self.populate_from_entry()

    def init_ui(self) -> None:
        """
        Build the form layout and dialog buttons.
        """

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.headword_input = QLineEdit()
        form_layout.addRow("Headword", self.headword_input)

        self.lemma_input = QLineEdit()
        form_layout.addRow("Lemma", self.lemma_input)

        self.homograph_spin = QSpinBox()
        self.homograph_spin.setRange(0, 99)
        self.homograph_spin.setValue(0)
        form_layout.addRow("Homograph Index", self.homograph_spin)

        self.provenance_combo = QComboBox()
        self.provenance_combo.addItems(PROVENANCE)
        form_layout.addRow("Provenance", self.provenance_combo)

        self.classification_combo = QComboBox()
        self.classification_combo.addItems(CLASSIFICATION)
        form_layout.addRow("Classification", self.classification_combo)

        main_layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.on_save)
        self.button_box.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box)

    def populate_from_entry(self) -> None:
        """
        Pre-fill form fields when editing an existing Entry.
        """

        if self.entry is None:
            return

        self.headword_input.setText(self.entry.headword)
        self.lemma_input.setText(self.entry.lemma)
        self.homograph_spin.setValue(self.entry.homograph_index)

        self.provenance_combo.setCurrentText(self.entry.provenance)
        self.classification_combo.setCurrentText(self.entry.classification)

    def on_save(self) -> None:
        """
        Validate the form and save the Entry.
        """

        headword = self.headword_input.text().strip()
        lemma = self.lemma_input.text().strip()

        if not headword or not lemma:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Headword and Lemma cannot be empty.",
            )
            return

        try:
            if self.entry is None:
                entry = Entry(
                    headword=headword,
                    lemma=lemma,
                    homograph_index=self.homograph_spin.value(),
                    provenance=self.provenance_combo.currentText(),
                    classification=self.classification_combo.currentText(),
                )
                create_entry(entry)
            else:
                self.entry.headword = headword
                self.entry.lemma = lemma
                self.entry.homograph_index = self.homograph_spin.value()
                self.entry.provenance = self.provenance_combo.currentText()
                self.entry.classification = self.classification_combo.currentText()
                update_entry(self.entry)

            self.accept()

        except (sqlite3.Error, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Database Error",
                str(exc),
            )


def main() -> None:
    """
    Launch the Entry Editor dialog for standalone testing.
    """

    app = QApplication(sys.argv)
    dialog = EntryEditorDialog()
    dialog.exec()


if __name__ == "__main__":
    main()