"""
తెలుగు మాటల అరయిక (TLRE)

Desktop Graphical User Interface

Version: 0.1.0
Reference Point: RP-006

Main application window for the Telugu Linguistic
Research Environment.
"""

from __future__ import annotations
from src.gui.entry_view import EntryInspectorDialog
import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.gui.entry_editor import EntryEditorDialog
from src.models import Entry
from src.queries import (
    find_entries_by_lemma,
    get_all_entries,
    get_entry_by_id,
)


class TLREMainWindow(QMainWindow):
    """
    Main window for the TLRE desktop application.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(
            "తెలుగు మాటల అరయిక (TLRE) — Linguistic Research Workspace"
        )

        self.resize(900, 600)

        self.init_ui()

        self.load_entries()

    def init_ui(self) -> None:
        """
        Construct the user interface.
        """

        # --------------------------------------------------
        # Central Widget
        # --------------------------------------------------

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # --------------------------------------------------
        # Search & Action Controls
        # --------------------------------------------------

        search_layout = QHBoxLayout()

        search_label = QLabel("Search:")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by lemma..."
        )

        self.search_button = QPushButton("Search")
        self.refresh_button = QPushButton("Refresh")
        self.add_entry_button = QPushButton("Add Entry")
        self.inspect_button = QPushButton("Inspect Entry")

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.refresh_button)
        search_layout.addWidget(self.add_entry_button)
        search_layout.addWidget(self.inspect_button)

        main_layout.addLayout(search_layout)

        # --------------------------------------------------
        # Entry Table
        # --------------------------------------------------

        self.table = QTableWidget()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Headword",
                "Lemma",
                "Homograph",
                "Provenance",
                "Classification",
            ]
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        main_layout.addWidget(self.table)

        # --------------------------------------------------
        # Status Bar
        # --------------------------------------------------

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_bar.showMessage("Ready.")

        # --------------------------------------------------
        # Signal Connections
        # --------------------------------------------------

        self.search_button.clicked.connect(self.on_search)
        self.refresh_button.clicked.connect(self.on_refresh)
        self.add_entry_button.clicked.connect(self.on_add_entry)
        self.inspect_button.clicked.connect(self.on_inspect_entry)
        self.search_input.returnPressed.connect(self.on_search)

        # Double-click row directly edits the entry
        self.table.cellDoubleClicked.connect(self.on_edit_entry)

    # --------------------------------------------------
    # Table Helpers
    # --------------------------------------------------

    def _set_table_item(
        self,
        row: int,
        column: int,
        value: object,
    ) -> None:
        """
        Safely set a table cell. None values are displayed as empty strings.
        """
        text = "" if value is None else str(value)

        self.table.setItem(
            row,
            column,
            QTableWidgetItem(text),
        )

    # --------------------------------------------------
    # Data Loading
    # --------------------------------------------------

    def load_entries(
        self,
        entries: list[Entry] | None = None,
    ) -> None:
        """
        Load entries into the table.
        """
        if entries is None:
            entries = get_all_entries()

        self.table.clearContents()
        self.table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            self._set_table_item(row, 0, entry.id)
            self._set_table_item(row, 1, entry.headword)
            self._set_table_item(row, 2, entry.lemma)
            self._set_table_item(row, 3, entry.homograph_index)
            self._set_table_item(row, 4, entry.provenance)
            self._set_table_item(row, 5, entry.classification)

        count = len(entries)
        label = "entry" if count == 1 else "entries"

        self.status_bar.showMessage(f"Loaded {count} {label}.")

    # --------------------------------------------------
    # Event Handlers
    # --------------------------------------------------

    def on_search(self) -> None:
        """
        Search for entries using the lemma.
        """
        search_text = self.search_input.text().strip()

        if not search_text:
            self.load_entries()
            return

        entries = find_entries_by_lemma(search_text)
        self.load_entries(entries)

    def on_refresh(self) -> None:
        """
        Reload every entry from the database.
        """
        self.search_input.clear()
        self.load_entries()

    def on_add_entry(self) -> None:
        """
        Open the Entry Editor in Create mode.
        """
        dialog = EntryEditorDialog(parent=self)

        if dialog.exec() == QDialog.Accepted:
            self.load_entries()

    def on_edit_entry(
        self,
        row: int,
        column: int,
    ) -> None:
        """
        Open the Entry Editor for the selected entry upon double-click.
        """
        item = self.table.item(row, 0)

        if item is None:
            return

        entry = get_entry_by_id(int(item.text()))

        if entry is None:
            return

        dialog = EntryEditorDialog(
            entry=entry,
            parent=self,
        )

        if dialog.exec() == QDialog.Accepted:
            self.load_entries()


    def on_inspect_entry(
        self,
        row: int | None = None,
        column: int | None = None,
    ) -> None:
        if row is None or isinstance(row, bool):
            row = self.table.currentRow()
        if row < 0:
            return

        item = self.table.item(row, 0)
        if item is None:
            return

        entry = get_entry_by_id(int(item.text()))
        if entry is None:
            return

        dialog = EntryInspectorDialog(entry=entry, parent=self)
        dialog.exec()


# ==========================================================
# Application Entry Point
# ==========================================================

def main() -> None:
    """
    Launch the TLRE desktop application.
    """
    app = QApplication(sys.argv)

    window = TLREMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()