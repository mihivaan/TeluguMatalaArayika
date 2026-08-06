"""
తెలుగు మాటల అరయిక (TLRE)

Claim Editor Dialog

Version: 0.2.0
Reference Point: RP-006

Dialog for creating and editing etymological claims.
"""

from __future__ import annotations

import sqlite3
import sys

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from src.constants import CLAIM_STATUSES
from src.models import Claim
from src.queries import (
    add_claim,
    update_claim,
)


class ClaimEditorDialog(QDialog):
    """
    Dialog for creating and editing Claim records.
    """

    def __init__(
        self,
        entry_id: int,
        claim: Claim | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.entry_id = entry_id
        self.claim = claim

        self.setModal(True)

        if self.claim is None:
            self.setWindowTitle("Add Claim")
        else:
            self.setWindowTitle("Edit Claim")

        self.resize(500, 320)

        self.init_ui()

        if self.claim is not None:
            self.populate_fields()

    def init_ui(self) -> None:
        """
        Construct the dialog user interface.
        """

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.claim_text_input = QLineEdit()
        self.claim_text_input.setPlaceholderText(
            "Enter claim statement..."
        )

        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.0, 1.0)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setDecimals(2)
        self.confidence_spin.setValue(1.0)

        self.status_combo = QComboBox()
        self.status_combo.addItems(CLAIM_STATUSES)

        self.rationale_input = QLineEdit()
        self.rationale_input.setPlaceholderText(
            "Optional research rationale..."
        )

        form_layout.addRow(
            "Claim:",
            self.claim_text_input,
        )
        form_layout.addRow(
            "Confidence:",
            self.confidence_spin,
        )
        form_layout.addRow(
            "Status:",
            self.status_combo,
        )
        form_layout.addRow(
            "Rationale:",
            self.rationale_input,
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
        Populate the dialog fields from an existing Claim.
        """

        assert self.claim is not None

        self.claim_text_input.setText(
            self.claim.claim_text
        )

        self.confidence_spin.setValue(
            self.claim.confidence
        )

        index = self.status_combo.findText(
            self.claim.status
        )

        if index >= 0:
            self.status_combo.setCurrentIndex(index)

        self.rationale_input.setText(
            self.claim.rationale or ""
        )

    def on_save(self) -> None:
        """
        Validate and save the Claim.
        """

        claim_text = self.claim_text_input.text().strip()

        if not claim_text:
            QMessageBox.critical(
                self,
                "Validation Error",
                "Claim text cannot be empty.",
            )
            return

        rationale = self.rationale_input.text().strip()

        if rationale == "":
            rationale = None

        try:

            if self.claim is None:

                new_claim = Claim(
                    entry_id=self.entry_id,
                    claim_text=claim_text,
                    confidence=self.confidence_spin.value(),
                    rationale=rationale,
                    status=self.status_combo.currentText(),
                )

                add_claim(new_claim)

            else:

                self.claim.claim_text = claim_text
                self.claim.confidence = (
                    self.confidence_spin.value()
                )
                self.claim.status = (
                    self.status_combo.currentText()
                )
                self.claim.rationale = rationale

                update_claim(self.claim)

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

    dialog = ClaimEditorDialog(
        entry_id=1,
    )

    dialog.exec()

    sys.exit(0)


if __name__ == "__main__":
    main()