"""
తెలుగు మాటల అరయిక (TLRE)

Application Trash Bin Workspace

Version: 0.2.1
Reference Point: RP-006

Dialog for viewing, restoring, and permanently purging soft-deleted entries.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models import Entry
from src.queries import delete_entry, get_deleted_entries, restore_entry


class TrashBinDialog(QDialog):
    """
    Dialog for inspecting and restoring soft-deleted entries.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("TLRE Trash Bin 🗑️ — Deleted Entries Archive")
        self.resize(800, 500)
        self.setModal(True)

        self.init_ui()
        self.load_deleted_entries()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Table of deleted entries
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Headword", "Lemma", "Provenance", "Classification"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # Control Buttons
        button_layout = QHBoxLayout()

        self.restore_button = QPushButton("Restore Selected Entry")
        self.restore_button.setStyleSheet(
            "padding: 6px 16px; background: #2F855A; color: white; font-weight: bold; border-radius: 4px;"
        )

        self.purge_button = QPushButton("Permanently Purge")
        self.purge_button.setStyleSheet(
            "padding: 6px 16px; background: #C53030; color: white; font-weight: bold; border-radius: 4px;"
        )

        self.close_button = QPushButton("Close")

        button_layout.addWidget(self.restore_button)
        button_layout.addWidget(self.purge_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        # Status Bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        # Connections
        self.restore_button.clicked.connect(self.on_restore)
        self.purge_button.clicked.connect(self.on_purge)
        self.close_button.clicked.connect(self.accept)

    def load_deleted_entries(self) -> None:
        entries = get_deleted_entries()
        self.table.clearContents()
        self.table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(str(entry.id)))
            self.table.setItem(row, 1, QTableWidgetItem(entry.headword))
            self.table.setItem(row, 2, QTableWidgetItem(entry.lemma))
            self.table.setItem(row, 3, QTableWidgetItem(entry.provenance))
            self.table.setItem(row, 4, QTableWidgetItem(entry.classification))

        count = len(entries)
        self.status_bar.showMessage(f"Trash Bin contains {count} deleted entry/entries.")

    def _selected_entry_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select an entry first.")
            return None

        item = self.table.item(row, 0)
        if item is None:
            return None

        try:
            return int(item.text())
        except ValueError:
            return None

    def on_restore(self) -> None:
        entry_id = self._selected_entry_id()
        if entry_id is None:
            return

        if restore_entry(entry_id):
            QMessageBox.information(self, "Restored", "Entry restored successfully!")
            self.load_deleted_entries()

    def on_purge(self) -> None:
        entry_id = self._selected_entry_id()
        if entry_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Permanent Purge",
            f"Are you sure you want to PERMANENTLY purge Entry ID {entry_id}?\n\nThis will permanently delete the entry and all its child meanings, claims, and notes. This cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if delete_entry(entry_id, hard_delete=True):
                QMessageBox.information(self, "Purged", "Entry permanently purged from database.")
                self.load_deleted_entries()


def main() -> None:
    app = QApplication(sys.argv)
    dialog = TrashBinDialog()
    dialog.exec()


if __name__ == "__main__":
    main()