"""
తెలుగు మాటల అరయిక (TLRE)

Entry Inspector Workspace

Version: 0.2.0
Reference Point: RP-006

Detailed inspector dialog for entries, meanings, claims,
research questions, and research notes.
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
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.gui.claim_editor import ClaimEditorDialog
from src.gui.meaning_editor import MeaningEditorDialog
from src.gui.note_editor import NoteEditorDialog
from src.gui.question_editor import QuestionEditorDialog
from src.models import Entry
from src.queries import (
    get_claims_for_entry,
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
        """
        Create the top summary card for the current Entry.
        """

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
        title_label.setAlignment(Qt.AlignLeft)

        headword_label = QLabel(f"Headword: {self.entry.headword}")
        lemma_label = QLabel(f"Lemma: {self.entry.lemma}")
        homograph_label = QLabel(f"Homograph Index: {self.entry.homograph_index}")
        provenance_label = QLabel(f"Provenance: {self.entry.provenance}")
        classification_label = QLabel(f"Classification: {self.entry.classification}")

        self.edit_entry_button = QPushButton("Edit Entry Core")

        top_row = QHBoxLayout()
        top_row.addWidget(title_label)
        top_row.addStretch(1)
        top_row.addWidget(self.edit_entry_button)

        header_layout.addLayout(top_row)
        header_layout.addWidget(headword_label)
        header_layout.addWidget(lemma_label)
        header_layout.addWidget(homograph_label)
        header_layout.addWidget(provenance_label)
        header_layout.addWidget(classification_label)

        self.main_layout.addWidget(self.header_card)

    def create_tabs(self) -> None:
        """
        Create the tabbed inspector workspace.
        """

        self.tab_widget = QTabWidget()

        # ==================================================
        # Meanings Tab
        # ==================================================

        meanings_widget = QWidget()
        meanings_layout = QVBoxLayout(meanings_widget)

        self.meanings_list = QListWidget()
        self.add_meaning_button = QPushButton("+ Meaning")

        meanings_layout.addWidget(self.meanings_list)
        meanings_layout.addWidget(self.add_meaning_button)

        self.tab_widget.addTab(meanings_widget, "Meanings")

        # ==================================================
        # Claims Tab
        # ==================================================

        claims_widget = QWidget()
        claims_layout = QVBoxLayout(claims_widget)

        self.claims_list = QListWidget()
        self.add_claim_button = QPushButton("+ Claim")

        claims_layout.addWidget(self.claims_list)
        claims_layout.addWidget(self.add_claim_button)

        self.tab_widget.addTab(claims_widget, "Claims")

        # ==================================================
        # Research Questions Tab
        # ==================================================

        questions_widget = QWidget()
        questions_layout = QVBoxLayout(questions_widget)

        self.questions_list = QListWidget()
        self.add_question_button = QPushButton("+ Question")

        questions_layout.addWidget(self.questions_list)
        questions_layout.addWidget(self.add_question_button)

        self.tab_widget.addTab(questions_widget, "Research Questions")

        # ==================================================
        # Journal Notes Tab
        # ==================================================

        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)

        self.notes_list = QListWidget()
        self.add_note_button = QPushButton("+ Note")

        notes_layout.addWidget(self.notes_list)
        notes_layout.addWidget(self.add_note_button)

        self.tab_widget.addTab(notes_widget, "Journal Notes")

        # ==================================================
        # Signal Connections
        # ==================================================

        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.add_meaning_button.clicked.connect(self.on_add_meaning)
        self.meanings_list.itemDoubleClicked.connect(self.on_edit_meaning)

        self.add_claim_button.clicked.connect(self.on_add_claim)
        self.claims_list.itemDoubleClicked.connect(self.on_edit_claim)

        self.add_question_button.clicked.connect(self.on_add_question)
        self.questions_list.itemDoubleClicked.connect(self.on_edit_question)

        self.add_note_button.clicked.connect(self.on_add_note)

        self.main_layout.addWidget(self.tab_widget)

        # Load initial tab data
        self.load_meanings()

    # --------------------------------------------------
    # Tab Loaders
    # --------------------------------------------------

    def load_meanings(self) -> None:
        """
        Load meanings for the current entry.
        """

        self.meanings_list.clear()

        meanings = get_meanings_for_entry(self.entry.id)

        for meaning in meanings:
            item = QListWidgetItem(
                f"{meaning.meaning_order}. {meaning.meaning}"
            )
            item.setData(Qt.UserRole, meaning)
            self.meanings_list.addItem(item)

    def load_claims(self) -> None:
        """
        Load claims for the current entry.
        """

        self.claims_list.clear()

        claims = get_claims_for_entry(self.entry.id)

        for claim in claims:
            item = QListWidgetItem(
                f"[{claim.status}] ({claim.confidence:.2f}) {claim.claim_text}"
            )
            if claim.rationale:
                item.setToolTip(claim.rationale)

            item.setData(Qt.UserRole, claim)
            self.claims_list.addItem(item)

    def load_questions(self) -> None:
        """
        Load research questions for the current entry and render parent-child tree branches.
        """

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

                item.setData(Qt.UserRole, question)
                self.questions_list.addItem(item)

                add_branch(
                    question.id,
                    depth + 1,
                )

        add_branch(None)

    def load_notes(self) -> None:
        """
        Load research journal notes.
        """

        self.notes_list.clear()

        notes = get_research_notes_for_entry(self.entry.id)

        for note in notes:

            timestamp = (
                str(note.created_at)
                if note.created_at is not None
                else ""
            )

            item = QListWidgetItem(f"[{timestamp}]\n{note.note_text}")
            item.setData(Qt.UserRole, note)
            self.notes_list.addItem(item)

    # --------------------------------------------------
    # Tab Events & Action Handlers
    # --------------------------------------------------

    def on_tab_changed(self, index: int) -> None:
        """
        Lazily load data for the selected tab.
        """

        if index == 0:
            self.load_meanings()
        elif index == 1:
            self.load_claims()
        elif index == 2:
            self.load_questions()
        elif index == 3:
            self.load_notes()

    def on_add_meaning(self) -> None:
        """
        Create a new Meaning for this Entry.
        """

        dialog = MeaningEditorDialog(
            entry_id=self.entry.id,
            parent=self,
        )

        if dialog.exec() == QDialog.Accepted:
            self.load_meanings()

    def on_edit_meaning(self, item: QListWidgetItem) -> None:
        """
        Edit an existing Meaning.
        """

        meaning = item.data(Qt.UserRole)

        if meaning is None:
            return

        dialog = MeaningEditorDialog(
            entry_id=self.entry.id,
            meaning=meaning,
            parent=self,
        )

        if dialog.exec() == QDialog.Accepted:
            self.load_meanings()

    def on_add_claim(self) -> None:
        """
        Create a new Claim for this Entry.
        """

        dialog = ClaimEditorDialog(
            entry_id=self.entry.id,
            parent=self,
        )

        if dialog.exec() == QDialog.Accepted:
            self.load_claims()

    def on_edit_claim(self, item: QListWidgetItem) -> None:
        """
        Edit an existing Claim.
        """

        claim = item.data(Qt.UserRole)

        if claim is None:
            return

        dialog = ClaimEditorDialog(
            entry_id=self.entry.id,
            claim=claim,
            parent=self,
        )

        if dialog.exec() == QDialog.Accepted:
            self.load_claims()

    def on_add_question(self) -> None:
        """
        Create a new Research Question for this Entry.
        """

        dialog = QuestionEditorDialog(
            entry_id=self.entry.id,
            parent=self,
        )

        if dialog.exec() == QDialog.Accepted:
            self.load_questions()

    def on_edit_question(self, item: QListWidgetItem) -> None:
        """
        Edit an existing Research Question.
        """

        question = item.data(Qt.UserRole)

        if question is None:
            return

        dialog = QuestionEditorDialog(
            entry_id=self.entry.id,
            question=question,
            parent=self,
        )

        if dialog.exec() == QDialog.Accepted:
            self.load_questions()

    def on_add_note(self) -> None:
        """
        Add a new timestamped research journal note for this Entry.
        """

        dialog = NoteEditorDialog(
            entry_id=self.entry.id,
            parent=self,
        )

        if dialog.exec() == QDialog.Accepted:
            self.load_notes()


# ==========================================================
# Standalone Runner
# ==========================================================

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