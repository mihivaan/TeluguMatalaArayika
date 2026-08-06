"""
తెలుగు మాటల అరయిక (TLRE)

Evidence Editor Dialog

Version: 0.2.0
Reference Point: RP-007

Dialog for attaching normalized evidence to claims via
Source -> Citation -> Evidence.
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

from src.constants import EVIDENCE_ROLES, EVIDENCE_TYPES
from src.models import Citation, Evidence
from src.queries import (
    add_evidence,
    create_citation,
    get_all_sources,
    get_citation_by_id,
    update_citation,
    update_evidence,
)


class EvidenceEditorDialog(QDialog):
    """
    Dialog for creating and editing Evidence records.
    """

    def __init__(
        self,
        claim_id: int,
        evidence: Evidence | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.claim_id = claim_id
        self.evidence = evidence

        self.setModal(True)

        if self.evidence is None:
            self.setWindowTitle("Attach Evidence to Claim")
        else:
            self.setWindowTitle("Edit Evidence")

        self.resize(600, 520)

        self.init_ui()

        if self.evidence is not None:
            self.populate_fields()

    def init_ui(self) -> None:
        """
        Construct the dialog user interface.
        """

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.source_combo = QComboBox()
        self._load_sources()

        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText("e.g. Page 412")

        self.column_ref_input = QLineEdit()
        self.column_ref_input.setPlaceholderText("e.g. Column 2")

        self.line_ref_input = QLineEdit()
        self.line_ref_input.setPlaceholderText("e.g. Line 15")

        self.paragraph_ref_input = QLineEdit()
        self.paragraph_ref_input.setPlaceholderText("e.g. Paragraph 3")

        self.citation_text_input = QLineEdit()
        self.citation_text_input.setPlaceholderText(
            "Verbatim quotation/excerpt from primary source..."
        )

        self.evidence_type_combo = QComboBox()
        self.evidence_type_combo.addItems(EVIDENCE_TYPES)

        self.evidence_role_combo = QComboBox()
        self.evidence_role_combo.addItems(EVIDENCE_ROLES)

        self.evidence_text_input = QLineEdit()
        self.evidence_text_input.setPlaceholderText(
            "Researcher's evidentiary synthesis/analysis..."
        )

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText(
            "Optional notes..."
        )

        form_layout.addRow("Source:", self.source_combo)
        form_layout.addRow("Page:", self.page_input)
        form_layout.addRow("Column Ref:", self.column_ref_input)
        form_layout.addRow("Line Ref:", self.line_ref_input)
        form_layout.addRow("Paragraph Ref:", self.paragraph_ref_input)
        form_layout.addRow("Citation Text:", self.citation_text_input)
        form_layout.addRow("Evidence Type:", self.evidence_type_combo)
        form_layout.addRow("Evidence Role:", self.evidence_role_combo)
        form_layout.addRow("Evidence Text:", self.evidence_text_input)
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.on_save)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _load_sources(self) -> None:
        """
        Populate the source combo with bibliographic sources.
        """
        self.source_combo.clear()

        sources = get_all_sources()

        for source in sources:
            label = source.name
            if source.author:
                label = f"{source.name} — {source.author}"
            self.source_combo.addItem(label, source.id)

    @staticmethod
    def _clean_optional_text(text: str) -> str | None:
        value = text.strip()
        return value if value else None

    def _set_combo_to_data(self, combo: QComboBox, data: object) -> bool:
        index = combo.findData(data)
        if index >= 0:
            combo.setCurrentIndex(index)
            return True
        return False

    def populate_fields(self) -> None:
        """
        Populate widgets from an existing Evidence record.
        """
        assert self.evidence is not None

        citation = get_citation_by_id(self.evidence.citation_id)
        if citation is None:
            QMessageBox.critical(
                self,
                "Data Error",
                "The linked citation could not be found.",
            )
            return

        if not self._set_combo_to_data(self.source_combo, citation.source_id):
            # Leave the combo at its default selection if the source is missing.
            pass

        self.page_input.setText(citation.page or "")
        self.column_ref_input.setText(citation.column_ref or "")
        self.line_ref_input.setText(citation.line_ref or "")
        self.paragraph_ref_input.setText(citation.paragraph_ref or "")
        self.citation_text_input.setText(citation.citation_text or "")

        self._set_combo_to_data(
            self.evidence_type_combo,
            self.evidence.evidence_type,
        )
        self._set_combo_to_data(
            self.evidence_role_combo,
            self.evidence.evidence_role,
        )

        self.evidence_text_input.setText(self.evidence.evidence_text)
        self.notes_input.setText(self.evidence.notes or "")

    def on_save(self) -> None:
        """
        Validate and save the Evidence / Citation pair.
        """
        citation_text = self.citation_text_input.text().strip()
        evidence_text = self.evidence_text_input.text().strip()

        if not citation_text:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Citation text cannot be empty.",
            )
            return

        if not evidence_text:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Evidence text cannot be empty.",
            )
            return

        selected_source_id = self.source_combo.currentData()
        if selected_source_id is None:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please select a source.",
            )
            return

        page = self._clean_optional_text(self.page_input.text())
        column_ref = self._clean_optional_text(self.column_ref_input.text())
        line_ref = self._clean_optional_text(self.line_ref_input.text())
        paragraph_ref = self._clean_optional_text(self.paragraph_ref_input.text())
        notes = self._clean_optional_text(self.notes_input.text())

        try:
            if self.evidence is None:
                citation = Citation(
                    source_id=int(selected_source_id),
                    page=page,
                    column_ref=column_ref,
                    line_ref=line_ref,
                    paragraph_ref=paragraph_ref,
                    citation_text=citation_text,
                )
                citation_id = create_citation(citation)

                evidence = Evidence(
                    claim_id=self.claim_id,
                    citation_id=citation_id,
                    evidence_type=self.evidence_type_combo.currentText(),
                    evidence_role=self.evidence_role_combo.currentText(),
                    evidence_text=evidence_text,
                    notes=notes,
                )
                add_evidence(evidence)

            else:
                citation = get_citation_by_id(self.evidence.citation_id)
                if citation is None:
                    raise ValueError("Linked citation could not be found.")

                citation.source_id = int(selected_source_id)
                citation.page = page
                citation.column_ref = column_ref
                citation.line_ref = line_ref
                citation.paragraph_ref = paragraph_ref
                citation.citation_text = citation_text

                citation_updated = update_citation(citation)
                if not citation_updated:
                    raise ValueError("Citation update failed.")

                self.evidence.claim_id = self.claim_id
                self.evidence.evidence_type = self.evidence_type_combo.currentText()
                self.evidence.evidence_role = self.evidence_role_combo.currentText()
                self.evidence.evidence_text = evidence_text
                self.evidence.notes = notes

                evidence_updated = update_evidence(self.evidence)
                if not evidence_updated:
                    raise ValueError("Evidence update failed.")

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

    dialog = EvidenceEditorDialog(
        claim_id=1,
    )
    dialog.exec()

    sys.exit(0)


if __name__ == "__main__":
    main()