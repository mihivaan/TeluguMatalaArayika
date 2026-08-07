"""
తెలుగు మాటల అరయిక (TLRE)

Desktop Graphical User Interface — Dual Workspace Architecture

Version: 0.2.1
Reference Point: RP-006

Main workspace featuring 'మాటల కాన్పెన' (Lexical Explorer) and
'దోఁటపు పట్టడ' (Data Workshop).
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
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
    QStackedWidget,
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
from src.gui.labels import LABELS
from src.gui.trash_bin import TrashBinDialog
from src.importers.csv_importer import import_entries_from_csv
from src.models import Entry
from src.queries import (
    delete_entry,
    find_entries_by_lemma,
    get_all_entries,
    get_entry_by_id,
)
from src.transliteration import rts_to_telugu


class TLREMainWindow(QMainWindow):
    """
    Main workspace window for TLRE.
    """

    def __init__(self) -> None:
        super().__init__()

        self.graph_window: LinguisticGraphWindow | None = None

        self.setWindowTitle(
            "తెలుగు మాటల అరయిక (TLRE) — Linguistic Research Workspace"
        )
        self.resize(1000, 650)

        self.init_ui()
        self.load_entries()

    def init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # --------------------------------------------------
        # 1. Top Workspace Mode Switcher
        # --------------------------------------------------
        mode_bar = QWidget()
        mode_bar.setStyleSheet(
            """
            QWidget {
                background: #EAE3D2;
                border-radius: 6px;
                padding: 4px;
            }
            QPushButton {
                padding: 6px 16px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:checked {
                background: #4A3B2E;
                color: white;
            }
            QPushButton:unchecked {
                background: transparent;
                color: #4A3B2E;
            }
            """
        )
        mode_layout = QHBoxLayout(mode_bar)
        mode_layout.setContentsMargins(4, 4, 4, 4)

        self.btn_exhibition_mode = QPushButton(LABELS["SHOWROOM_TITLE"])
        self.btn_exhibition_mode.setCheckable(True)
        self.btn_exhibition_mode.setChecked(True)

        self.btn_lab_mode = QPushButton(LABELS["WORKSHOP_TITLE"])
        self.btn_lab_mode.setCheckable(True)

        mode_layout.addWidget(self.btn_exhibition_mode)
        mode_layout.addWidget(self.btn_lab_mode)
        mode_layout.addStretch(1)

        main_layout.addWidget(mode_bar)

        # --------------------------------------------------
        # 2. Stacked Toolbar (Exhibition vs Workshop)
        # --------------------------------------------------
        self.toolbar_stack = QStackedWidget()

        # MODE 1: EXPLOER (మాటల కాన్పెన)
        exhibition_page = QWidget()
        exhibition_layout = QVBoxLayout(exhibition_page)
        exhibition_layout.setContentsMargins(0, 0, 0, 0)

        search_row = QHBoxLayout()
        search_label = QLabel("<b>వెతుకు:</b>")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(LABELS["SEARCH_PLACEHOLDER"])

        self.search_button = QPushButton(LABELS["SEARCH_BUTTON"])
        self.refresh_button = QPushButton(LABELS["REFRESH_BUTTON"])
        self.inspect_button = QPushButton(LABELS["INSPECT_BUTTON"])
        self.graph_button = QPushButton(LABELS["GRAPH_BUTTON"])
        self.export_button = QPushButton(LABELS["EXPORT_BUTTON"])

        search_row.addWidget(search_label)
        search_row.addWidget(self.search_input, stretch=1)  # Full width!
        search_row.addWidget(self.search_button)
        search_row.addWidget(self.refresh_button)
        search_row.addWidget(self.inspect_button)
        search_row.addWidget(self.graph_button)
        search_row.addWidget(self.export_button)

        exhibition_layout.addLayout(search_row)
        self.toolbar_stack.addWidget(exhibition_page)

        # MODE 2: WORKSHOP (దోఁటపు పట్టడ)
        lab_page = QWidget()
        lab_layout = QHBoxLayout(lab_page)
        lab_layout.setContentsMargins(0, 0, 0, 0)

        lab_label = QLabel("<b>పట్టడ పనులు:</b>")
        self.add_entry_button = QPushButton(LABELS["ADD_ENTRY_BUTTON"])
        self.import_button = QPushButton(LABELS["IMPORT_BUTTON"])
        self.trash_button = QPushButton(LABELS["TRASH_BUTTON"])

        self.delete_button = QPushButton(LABELS["DELETE_BUTTON"])
        self.delete_button.setStyleSheet(
            "padding: 6px 12px; background: #C53030; color: white; font-weight: bold; border-radius: 4px;"
        )

        lab_layout.addWidget(lab_label)
        lab_layout.addWidget(self.add_entry_button)
        lab_layout.addWidget(self.import_button)
        lab_layout.addWidget(self.trash_button)
        lab_layout.addStretch(1)
        lab_layout.addWidget(self.delete_button)

        self.toolbar_stack.addWidget(lab_page)
        main_layout.addWidget(self.toolbar_stack)

        # --------------------------------------------------
        # 3. Main Word Explorer Grid
        # --------------------------------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "తలమాట", "తొంటడ", "Homograph", "Provenance", "Classification"]
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        main_layout.addWidget(self.table)

        # --------------------------------------------------
        # 4. Status Bar
        # --------------------------------------------------
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("సిద్ధముగా ఉన్నది (Ready).")

        # --------------------------------------------------
        # 5. Signal Connections
        # --------------------------------------------------
        self.btn_exhibition_mode.clicked.connect(self.on_switch_to_exhibition)
        self.btn_lab_mode.clicked.connect(self.on_switch_to_lab)

        self.search_button.clicked.connect(self.on_search)
        self.refresh_button.clicked.connect(self.on_refresh)
        self.inspect_button.clicked.connect(self.on_inspect_entry)
        self.graph_button.clicked.connect(self.on_open_graph)
        self.export_button.clicked.connect(self.on_export_entry)
        self.search_input.returnPressed.connect(self.on_search)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.table.cellDoubleClicked.connect(self.on_edit_entry)

        self.add_entry_button.clicked.connect(self.on_add_entry)
        self.import_button.clicked.connect(self.on_import_csv)
        self.trash_button.clicked.connect(self.on_open_trash_bin)
        self.delete_button.clicked.connect(self.on_delete_entry)

    def on_switch_to_exhibition(self) -> None:
        self.btn_exhibition_mode.setChecked(True)
        self.btn_lab_mode.setChecked(False)
        self.toolbar_stack.setCurrentIndex(0)
        self.status_bar.showMessage("కూర్పు: 📚 మాటల కాన్పెన (Lexical Explorer)")

    def on_switch_to_lab(self) -> None:
        self.btn_exhibition_mode.setChecked(False)
        self.btn_lab_mode.setChecked(True)
        self.toolbar_stack.setCurrentIndex(1)
        self.status_bar.showMessage("కూర్పు: 🛠️ దోఁటపు పట్టడ (Data Workshop)")

    def _set_table_item(self, row: int, column: int, value: object) -> None:
        text = "" if value is None else str(value)
        self.table.setItem(row, column, QTableWidgetItem(text))

    def load_entries(self, entries: list[Entry] | None = None) -> None:
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
        self.status_bar.showMessage(f"చేరిన తలమాటలు: {count}")

    def on_search_text_changed(self, text: str) -> None:
        search_text = text.strip()
        if not search_text:
            self.status_bar.showMessage("సిద్ధముగా ఉన్నది.")
            return

        telugu = rts_to_telugu(search_text)
        if telugu != search_text:
            self.status_bar.showMessage(f"పలుకుబడి → {telugu}")
        else:
            self.status_bar.showMessage("సిద్ధముగా ఉన్నది.")

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
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_entries()

    def on_inspect_entry(self, row: int | None = None, column: int | None = None) -> None:
        if row is None or isinstance(row, bool):
            row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "ఎంపిక లేకపోయింది", "దయచేసి ఒక తలమాటను ఎంచుకోండి.")
            return

        item = self.table.item(row, 0)
        if item is None:
            return

        entry = get_entry_by_id(int(item.text()))
        if entry is None:
            return

        dialog = EntryInspectorDialog(entry=entry, parent=self)
        dialog.exec()

    def on_edit_entry(self, row: int, column: int) -> None:
        item = self.table.item(row, 0)
        if item is None:
            return

        entry = get_entry_by_id(int(item.text()))
        if entry is None:
            return

        dialog = EntryEditorDialog(entry=entry, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_entries()

    def on_open_graph(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "ఎంపిక లేకపోయింది", "దయచేసి ఒక తలమాటను ఎంచుకోండి.")
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
            self, "దిగుమతి చేసుకునే CSV ఫైలును ఎంచుకోండి", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            inserted, skipped = import_entries_from_csv(file_path)
        except Exception as exc:
            QMessageBox.critical(self, "దిగుమతి విఫలమైనది", str(exc))
            return

        QMessageBox.information(
            self,
            "దిగుమతి పూర్తయినది",
            f"దిగుమతి వివరాలు:\nచేర్చబడినవి: {inserted}\nవదలివేయబడినవి (నకిలీలు): {skipped}",
        )
        self.load_entries()

    def on_export_entry(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "ఎంపిక లేకపోయింది", "దయచేసి ఎగుమతి చేయడానికి ఒక తలమాటను ఎంచుకోండి.")
            return

        item = self.table.item(row, 0)
        if item is None:
            return

        entry = get_entry_by_id(int(item.text()))
        if entry is None:
            return

        default_name = f"{entry.lemma}_export.md"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "పరిశోధనా సమాచారమును ఎగుమతి చేయండి",
            default_name,
            "Markdown Files (*.md);;JSON Files (*.json)",
        )
        if not file_path:
            return

        format_type = "json" if file_path.lower().endswith(".json") else "markdown"
        if format_type == "markdown" and not file_path.lower().endswith(".md"):
            file_path += ".md"

        try:
            export_entry_to_file(entry.id, file_path, format_type=format_type)
        except Exception as exc:
            QMessageBox.critical(self, "ఎగుమతి విఫలమైనది", str(exc))
            return

        QMessageBox.information(
            self, "ఎగుమతి విజయవంతమైనది", f"పరిశోధనా సమాచారము ఎగుమతి చేయబడినది:\n{file_path}"
        )

    def on_open_trash_bin(self) -> None:
        dialog = TrashBinDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_entries()

    def on_delete_entry(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "ఎంపిక లేకపోయింది", "దయచేసి తొలగించడానికి ఒక తలమాటను ఎంచుకోండి.")
            return

        item = self.table.item(row, 0)
        if item is None:
            return

        entry_id = int(item.text())
        reply = QMessageBox.question(
            self,
            "తుక్కు బుట్టకు పంపుటకు నిర్ధారణ",
            f"తలమాట ఐడీ {entry_id} ను తుక్కు బుట్టకు పంపాలనుకుంటున్నారా?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if delete_entry(entry_id, hard_delete=False):
                QMessageBox.information(
                    self, "తుక్కు బుట్టకు పంపబడినది", "తలమాట తుక్కు బుట్టకు పంపబడినది. మీరు ఎప్పుడైనా పునరుద్ధరించుకోవచ్చు!"
                )
                self.load_entries()


def main() -> None:
    app = QApplication(sys.argv)
    window = TLREMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()