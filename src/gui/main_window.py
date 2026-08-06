"""
తెలుగు మాటల అరయిక (TLRE)

Desktop Graphical User Interface

Version: 0.1.0
Reference Point: RP-006

Main application window for the Telugu Linguistic
Research Environment.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.export import export_entry_to_file
from src.gui.entry_editor import EntryEditorDialog
from src.gui.entry_view import EntryInspectorDialog
from src.gui.graph_view import LinguisticGraphWindow
from src.importers.csv_importer import import_entries_from_csv
from src.models import Entry
from src.queries import (
    find_entries_by_lemma,
    get_all_entries,
    get_entry_by_id,
)
from src.transliteration import rts_to_telugu


class TLREMainWindow(QMainWindow):
    """
    Main window for the TLRE desktop application.
    """

    def __init__(self) -> None:
        super().__init__()

        self.graph_window: LinguisticGraphWindow | None = None

        self.setWindowTitle(
            "తెలుగు మాటల అరయిక (TLRE) — Linguistic Research Workspace"
        )

        self.resize(950, 600)

        self.init_ui()

        self.load_entries()

    def init_ui(self) -> None:
        """
        Construct the user interface.
        """

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Search & Action Controls
        search_layout = QHBoxLayout()

        search_label = QLabel("Search:")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by lemma...")

        self.search_button = QPushButton("Search")
        self.refresh_button = QPushButton("Refresh")
        self.add_entry_button = QPushButton("Add Entry")
        self.inspect_button = QPushButton("Inspect Entry")
        self.graph_button = QPushButton("Open Graph")
        self.import_button = QPushButton("Import CSV")
        self.export_button = QPushButton("Export Record")

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.refresh_button)
        search_layout.addWidget(self.add_entry_button)
        search_layout.addWidget(self.inspect_button)
        search_layout.addWidget(self.graph_button)
        search_layout.addWidget(self.import_button)
        search_layout.addWidget(self.export_button)

        main_layout.addLayout(search_layout)

        # Entry Table
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
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.setSelectionMode(QTableWidget.SingleSelection)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        main_layout.addWidget(self.table)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_bar.showMessage("Ready.")

        # Signal Connections
        self.search_button.clicked.connect(self.on_search)
        self.refresh_button.clicked.connect(self.on_refresh)
        self.add_entry_button.clicked.connect(self.on_add_entry)
        self.inspect_button.clicked.connect(self.on_inspect_entry)
        self.graph_button.clicked.connect(self.on_open_graph)
        self.import_button.clicked.connect(self.on_import_csv)
        self.export_button.clicked.connect(self.on_export_entry)

        self.search_input.returnPressed.connect(self.on_search)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.table.cellDoubleClicked.connect(self.on_inspect_entry)

    def _set_table_item(
        self,
        row: int,
        column: int,
        value: object,
    ) -> None:
        text = "" if value is None else str(value)

        self.table.setItem(
            row,
            column,
            QTableWidgetItem(text),
        )

    def load_entries(
        self,
        entries: list[Entry] | None = None,
    ) -> None:
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

    def on_search_text_changed(self, text: str) -> None:
        search_text = text.strip()
        if not search_text:
            self.status_bar.showMessage("Ready.")
            return

        telugu = rts_to_telugu(search_text)
        if telugu != search_text:
            self.status_bar.showMessage(f"Phonetic → {telugu}")
        else:
            self.status_bar.showMessage("Ready.")

    def on_search(self) -> None:
        search_text = self.search_input.text().strip()

        if not search_text:
            self.load_entries()
            return

        entries = find_entries_by_lemma(search_text)
        if not entries:
            entries = find_entries_by_lemma(rts_to_telugu(search_text))

        self.load_entries(entries)

    def on_refresh(self) -> None:
        self.search_input.clear()
        self.load_entries()

    def on_add_entry(self) -> None:
        dialog = EntryEditorDialog(parent=self)

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

        dialog = EntryInspectorDialog(
            entry=entry,
            parent=self,
        )

        dialog.exec()

    def on_open_graph(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return

        item = self.table.item(row, 0)
        if item is None:
            return

        try:
            entry_id = int(item.text())
        except ValueError:
            return

        self.graph_window = LinguisticGraphWindow(parent=self)
        self.graph_window.load_graph_for_entry(entry_id)
        self.graph_window.show()
        self.graph_window.raise_()
        self.graph_window.activateWindow()

    def on_import_csv(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File to Import",
            "",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            inserted, skipped = import_entries_from_csv(file_path)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Import Failed",
                str(exc),
            )
            return

        QMessageBox.information(
            self,
            "Import Complete",
            (
                "Import summary:\n"
                f"Inserted: {inserted}\n"
                f"Skipped (duplicates): {skipped}"
            ),
        )

        self.load_entries()

    def on_export_entry(self) -> None:
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select an entry to export.",
            )
            return

        item = self.table.item(row, 0)

        if item is None:
            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select an entry to export.",
            )
            return

        entry = get_entry_by_id(int(item.text()))

        if entry is None:
            QMessageBox.warning(
                self,
                "Export Failed",
                "Unable to retrieve the selected entry.",
            )
            return

        default_name = f"{entry.lemma}_export.md"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Research Record",
            default_name,
            "Markdown Files (*.md);;JSON Files (*.json)",
        )

        if not file_path:
            return

        format_type = "json" if file_path.lower().endswith(".json") else "markdown"

        if format_type == "markdown" and not file_path.lower().endswith(".md"):
            file_path += ".md"

        try:
            export_entry_to_file(
                entry.id,
                file_path,
                format_type=format_type,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Export Failed",
                str(exc),
            )
            return

        QMessageBox.information(
            self,
            "Export Successful",
            f"Research record exported to:\n{file_path}",
        )


def main() -> None:
    app = QApplication(sys.argv)

    window = TLREMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()