"""
తెలుగు మాటల అరయిక (TLRE)

Desktop Graphical User Interface

Version: 0.1.0
Reference Point: RP-006

Main application window for the Telugu Linguistic
Research Environment.
"""

from __future__ import annotations
from src.models import Entry

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QLabel,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.queries import (
    find_entries_by_lemma,
    get_all_entries,
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
        # Search Controls
        # --------------------------------------------------

        search_layout = QHBoxLayout()

        search_label = QLabel("Search:")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by lemma..."
        )

        self.search_button = QPushButton("Search")
        self.refresh_button = QPushButton("Refresh")

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.refresh_button)

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

        self.status_bar.showMessage(
            "Ready."
        )

        # --------------------------------------------------
        # Signal Connections
        # --------------------------------------------------

        self.search_button.clicked.connect(
            self.on_search
        )

        self.refresh_button.clicked.connect(
            self.on_refresh
        )

        self.search_input.returnPressed.connect(
            self.on_search
        )

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
        Safely set a table cell.

        None values are displayed as empty strings.
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
        entries: list | None = None,
    ) -> None:
        """
        Load entries into the table.

        If entries is None, all entries are loaded
        from the database.
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

        self.status_bar.showMessage(
            f"Loaded {count} {label}."
        )

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


# ==========================================================
# Application Entry Point
# ==========================================================

def main() -> None:
    """
    Launch the TLRE desktop application.
    """

    import sys

    app = QApplication(sys.argv)

    window = TLREMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()