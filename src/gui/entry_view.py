"""\
తెలుగు మాటల అరయిక (TLRE)

Entry Inspector Workspace

Version: 0.2.0
Reference Point: RP-006

Detailed inspector dialog for entries, meanings, claims,
research questions, research notes, and evidence.
"""

from __future__ import annotations

import sqlite3
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.gui.entry_editor import EntryEditorDialog
from src.queries import get_entry_by_id  
from src.gui.claim_editor import ClaimEditorDialog
from src.gui.evidence_editor import EvidenceEditorDialog
from src.gui.graph_view import LinguisticGraphWindow
from src.gui.meaning_editor import MeaningEditorDialog
from src.gui.note_editor import NoteEditorDialog
from src.gui.question_editor import QuestionEditorDialog
from src.models import Entry
from src.queries import (
    get_claims_for_entry,
    get_evidence_for_claim,
    get_meanings_for_entry,
    get_research_notes_for_entry,
    get_research_questions_for_entry,
)


class EntryInspectorDialog(QDialog):
    """
    Detailed inspector dialog for a single Entry.
    """

    def __init__(self, entry: Entry, parent=None) -> None:
        super().__init__(parent)

        self.entry = entry
        self.graph_window: LinguisticGraphWindow | None = None

        self.setWindowTitle(
            f"Linguistic Inspector — {self.entry.headword} (Lemma: {self.entry.lemma})"
        )
        self.resize(850, 600)
        self.setModal(True)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(12)

        self.create_header()
        self.create_tabs()

    def create_header(self) -> None:
        self.header_card = QGroupBox()
        self.header_card.setObjectName("headerCard")

        self.header_card.setStyleSheet(
            """
            QGroupBox#headerCard {
                border: 1px solid #cfcfcf;
                border-radius: 10px;
                padding: 10px;
                background: #fafafa;
            }
            QLabel#headerLabelTitle {
                font-weight: 700;
            }
            """
        )

        header_layout = QVBoxLayout(self.header_card)
        header_layout.setSpacing(6)

        title_label = QLabel("Entry Overview")
        title_label.setObjectName("headerLabelTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        headword_label = QLabel(f"Headword: {self.entry.headword}")
        lemma_label = QLabel(f"Lemma: {self.entry.lemma}")
        homograph_label = QLabel(f"Homograph Index: {self.entry.homograph_index}")
        provenance_label = QLabel(f"Provenance: {self.entry.provenance}")
        classification_label = QLabel(f"Classification: {self.entry.classification}")

        self.edit_entry_button = QPushButton("Edit Entry Core")
        self.edit_entry_button.clicked.connect(self.on_edit_entry_core)
        self.open_graph_button = QPushButton("Open Graph View")

        top_row = QHBoxLayout()
        top_row.addWidget(title_label)
        top_row.addStretch(1)
        top_row.addWidget(self.edit_entry_button)
        top_row.addWidget(self.open_graph_button)

        header_layout.addLayout(top_row)
        header_layout.addWidget(headword_label)
        header_layout.addWidget(lemma_label)
        header_layout.addWidget(homograph_label)
        header_layout.addWidget(provenance_label)
        header_layout.addWidget(classification_label)

        self.main_layout.addWidget(self.header_card)

        self.open_graph_button.clicked.connect(self.on_open_graph)

    def create_tabs(self) -> None:
        self.tab_widget = QTabWidget()

        # Meanings Tab
        meanings_widget = QWidget()
        meanings_layout = QVBoxLayout(meanings_widget)

        self.meanings_list = QListWidget()
        self.add_meaning_button = QPushButton("+ Meaning")

        meanings_layout.addWidget(self.meanings_list)
        meanings_layout.addWidget(self.add_meaning_button)

        self.tab_widget.addTab(meanings_widget, "Meanings")

        # Claims Tab
        claims_widget = QWidget()
        claims_layout = QVBoxLayout(claims_widget)

        self.claims_list = QListWidget()
        self.add_claim_button = QPushButton("+ Claim")
        self.add_evidence_button = QPushButton("+ Evidence")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_claim_button)
        button_layout.addWidget(self.add_evidence_button)

        claims_layout.addWidget(self.claims_list)
        claims_layout.addLayout(button_layout)

        self.tab_widget.addTab(claims_widget, "Claims")

        # Research Questions Tab
        questions_widget = QWidget()
        questions_layout = QVBoxLayout(questions_widget)

        self.questions_list = QListWidget()
        self.add_question_button = QPushButton("+ Question")

        questions_layout.addWidget(self.questions_list)
        questions_layout.addWidget(self.add_question_button)

        self.tab_widget.addTab(questions_widget, "Research Questions")

        # Journal Notes Tab
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)

        self.notes_list = QListWidget()
        self.add_note_button = QPushButton("+ Note")

        notes_layout.addWidget(self.notes_list)
        notes_layout.addWidget(self.add_note_button)

        self.tab_widget.addTab(notes_widget, "Journal Notes")

        # Signal Connections
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.add_meaning_button.clicked.connect(self.on_add_meaning)
        self.meanings_list.itemDoubleClicked.connect(self.on_edit_meaning)

        self.add_claim_button.clicked.connect(self.on_add_claim)
        self.claims_list.itemDoubleClicked.connect(self.on_edit_claim)

        self.add_evidence_button.clicked.connect(self.on_add_evidence)

        self.add_question_button.clicked.connect(self.on_add_question)
        self.questions_list.itemDoubleClicked.connect(self.on_edit_question)

        self.add_note_button.clicked.connect(self.on_add_note)

        self.main_layout.addWidget(self.tab_widget)

        self.load_meanings()

    def load_meanings(self) -> None:
        self.meanings_list.clear()

        meanings = get_meanings_for_entry(self.entry.id)

        for meaning in meanings:
            item = QListWidgetItem(
                f"{meaning.meaning_order}. {meaning.meaning}"
            )
            item.setData(Qt.ItemDataRole.UserRole, meaning)
            self.meanings_list.addItem(item)

    def load_claims(self) -> None:
        self.claims_list.clear()

        claims = get_claims_for_entry(self.entry.id)

        for claim in claims:
            claim_item = QListWidgetItem(
                f"[{claim.status}] ({claim.confidence:.2f}) {claim.claim_text}"
            )

            if claim.rationale:
                claim_item.setToolTip(claim.rationale)

            claim_item.setData(Qt.ItemDataRole.UserRole, claim)
            self.claims_list.addItem(claim_item)

            evidence_list = get_evidence_for_claim(claim.id)

            for evidence in evidence_list:
                evidence_text = (
                    f"    └─ [{evidence.evidence_role}] "
                    f"{evidence.evidence_text}"
                )

                evidence_item = QListWidgetItem(evidence_text)
                evidence_item.setFlags(
                    evidence_item.flags() & ~Qt.ItemFlag.ItemIsSelectable
                )
                evidence_item.setToolTip(f"Evidence ID: {evidence.id}")

                self.claims_list.addItem(evidence_item)

    def load_questions(self) -> None:
        self.questions_list.clear()

        questions = get_research_questions_for_entry(self.entry.id)

        children: dict[int | None, list] = {}

        for question in questions:
            children.setdefault(
                question.parent_question_id,
                [],
            ).append(question)

        def add_branch(
            parent_id: int | None,
            depth: int = 0,
        ) -> None:
            for question in children.get(parent_id, []):

                indent = "    " * depth

                text = f"{indent}[{question.status}] {question.question_text}"

                item = QListWidgetItem(text)

                if question.resolution_summary:
                    item.setToolTip(question.resolution_summary)

                item.setData(Qt.ItemDataRole.UserRole, question)
                self.questions_list.addItem(item)

                add_branch(
                    question.id,
                    depth + 1,
                )

        add_branch(None)

    def load_notes(self) -> None:
        self.notes_list.clear()

        notes = get_research_notes_for_entry(self.entry.id)

        for note in notes:

            timestamp = (
                str(note.created_at)
                if note.created_at is not None
                else ""
            )

            item = QListWidgetItem(f"[{timestamp}]\n{note.note_text}")
            item.setData(Qt.ItemDataRole.UserRole, note)
            self.notes_list.addItem(item)

    def on_tab_changed(self, index: int) -> None:
        if index == 0:
            self.load_meanings()
        elif index == 1:
            self.load_claims()
        elif index == 2:
            self.load_questions()
        elif index == 3:
            self.load_notes()

    def on_add_meaning(self) -> None:
        dialog = MeaningEditorDialog(
            entry_id=self.entry.id,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_meanings()

    def on_edit_meaning(self, item: QListWidgetItem) -> None:
        meaning = item.data(Qt.ItemDataRole.UserRole)

        if meaning is None:
            return

        dialog = MeaningEditorDialog(
            entry_id=self.entry.id,
            meaning=meaning,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_meanings()

    def on_add_claim(self) -> None:
        dialog = ClaimEditorDialog(
            entry_id=self.entry.id,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_claims()

    def on_edit_claim(self, item: QListWidgetItem) -> None:
        claim = item.data(Qt.ItemDataRole.UserRole)

        if claim is None:
            return

        dialog = ClaimEditorDialog(
            entry_id=self.entry.id,
            claim=claim,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_claims()

    def on_add_evidence(self) -> None:
        item = self.claims_list.currentItem()

        if item is None:
            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select a claim first to attach evidence.",
            )
            return

        claim = item.data(Qt.ItemDataRole.UserRole)

        if claim is None:
            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select a claim first to attach evidence.",
            )
            return

        dialog = EvidenceEditorDialog(
            claim_id=claim.id,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_claims()

    def on_add_question(self) -> None:
        dialog = QuestionEditorDialog(
            entry_id=self.entry.id,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_questions()

    def on_edit_question(self, item: QListWidgetItem) -> None:
        question = item.data(Qt.ItemDataRole.UserRole)

        if question is None:
            return

        dialog = QuestionEditorDialog(
            entry_id=self.entry.id,
            question=question,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_questions()

    def on_add_note(self) -> None:
        dialog = NoteEditorDialog(
            entry_id=self.entry.id,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_notes()

    def on_open_graph(self) -> None:
        if self.entry.id is None:
            return

        self.graph_window = LinguisticGraphWindow(parent=self)
        self.graph_window.load_graph_for_entry(int(self.entry.id))
        self.graph_window.show()
        self.graph_window.raise_()
        self.graph_window.activateWindow()

    def refresh_header_labels(self) -> None:
        """
        Update header card text labels after editing core entry fields.
        """
        # Find child labels in header_card or update them
        for widget in self.header_card.findChildren(QLabel):
            txt = widget.text()
            if txt.startswith("Headword:"):
                widget.setText(f"Headword: {self.entry.headword}")
            elif txt.startswith("Lemma:"):
                widget.setText(f"Lemma: {self.entry.lemma}")
            elif txt.startswith("Homograph Index:"):
                widget.setText(f"Homograph Index: {self.entry.homograph_index}")
            elif txt.startswith("Provenance:"):
                widget.setText(f"Provenance: {self.entry.provenance}")
            elif txt.startswith("Classification:"):
                widget.setText(f"Classification: {self.entry.classification}")

    def on_edit_entry_core(self) -> None:
        """
        Launch the EntryEditorDialog to edit the core entry fields.
        """
        dialog = EntryEditorDialog(entry=self.entry, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Re-fetch updated entry from database
            updated = get_entry_by_id(int(self.entry.id))
            if updated:
                self.entry = updated
                self.refresh_header_labels()
                self.setWindowTitle(
                    f"Linguistic Inspector — {self.entry.headword} (Lemma: {self.entry.lemma})"
                )


def main() -> None:
    app = QApplication(sys.argv)

    sample_entry = Entry(
        id=1,
        headword="Sample",
        lemma="Sample",
        homograph_index=0,
        provenance="Unknown",
        classification="Unknown",
    )

    dialog = EntryInspectorDialog(sample_entry)
    dialog.exec()

    sys.exit(0)


if __name__ == "__main__":
    main()