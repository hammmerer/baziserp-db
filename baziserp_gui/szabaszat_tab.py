from datetime import date
import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QLineEdit, QDateEdit, QPushButton, QCheckBox, QApplication, QSizePolicy, QMessageBox,
    QMenu, QToolButton, QComboBox, QStyle, QStyledItemDelegate
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QDate, QTimer

DATA_FILE = "megrendelesek.json"

class SzabaszatTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)

        top_layout = QHBoxLayout()
        self.search_entry = QLineEdit()
        self.search_entry.setFixedWidth(150)
        self.search_entry.setPlaceholderText("Keresés...")
        self.search_entry.textChanged.connect(self.filter_and_highlight_table)
        top_layout.addStretch()
        top_layout.addWidget(self.search_entry)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Rendezés: munkaszám A-Z", "Rendezés: határidő A-Z"])
        self.sort_combo.currentIndexChanged.connect(self.sort_table)
        top_layout.addWidget(self.sort_combo)

        main_layout.addLayout(top_layout)

        form_wrapper = QWidget()
        form_layout = QHBoxLayout(form_wrapper)
        form_wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        form_layout.addWidget(QLabel("Munkaszám:"))
        self.entry_munkaszam = QLineEdit()
        form_layout.addWidget(self.entry_munkaszam)

        form_layout.addWidget(QLabel("Megrendelő neve:"))
        self.entry_megrendelo = QLineEdit()
        form_layout.addWidget(self.entry_megrendelo)

        form_layout.addWidget(QLabel("Felvétel dátuma:"))
        self.date_felvetel = QDateEdit()
        self.date_felvetel.setDate(QDate.currentDate())
        self.date_felvetel.setCalendarPopup(True)
        self.date_felvetel.dateChanged.connect(self.update_hatarido)
        form_layout.addWidget(self.date_felvetel)

        form_layout.addWidget(QLabel("Határidő:"))
        self.date_hatarido = QDateEdit()
        self.date_hatarido.setDate(self.add_workdays(QDate.currentDate(), 13))
        self.date_hatarido.setCalendarPopup(True)
        form_layout.addWidget(self.date_hatarido)

        self.add_button = QPushButton("Új megrendelés felvétele")
        self.add_button.setFixedWidth(250)
        self.add_button.setDefault(True)
        self.add_button.clicked.connect(self.add_row_to_table)
        form_layout.addWidget(self.add_button)

        self.entry_munkaszam.returnPressed.connect(self.add_button.click)
        self.entry_megrendelo.returnPressed.connect(self.add_button.click)

        main_layout.addWidget(form_wrapper)

        self.table = QTableWidget()
        self.table.setColumnCount(22)
        self.table.setHorizontalHeaderLabels([
            "✓", "Munkaszám", "Megrendelő neve", "Felvétel dátuma",
            "Határidő", "Hátralévő napok",
            "116-18", "116-16",
            "HF", "kód",
            "db", "kód","db", "kód","db",
            "Össz. tábla", "Átadva", "Levágva",
            "Élzárva", "Egyéb munkák", "Kész", "", ":"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setColumnWidth(0, 25)
        self.table.setColumnWidth(1, 70)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 70)
        self.table.setColumnWidth(4, 70)
        self.table.setColumnWidth(5, 30)
        self.table.setColumnWidth(6, 30)
        self.table.setColumnWidth(7, 30)
        self.table.setColumnWidth(8, 30)
        self.table.setColumnWidth(9, 70)
        self.table.setColumnWidth(10, 40)
        self.table.setColumnWidth(11, 70)
        self.table.setColumnWidth(12, 40)
        self.table.setColumnWidth(13, 70)
        self.table.setColumnWidth(14, 40)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        self.load_table_data()
        QTimer.singleShot(10, self.highlight_duplicates)

    def add_workdays(self, start_date: QDate, days: int) -> QDate:
        current = QDate(start_date)
        added = 0
        while added < days:
            current = current.addDays(1)
            if current.dayOfWeek() < 6:
                added += 1
        return current

    def update_hatarido(self):
        self.date_hatarido.setDate(self.add_workdays(self.date_felvetel.date(), 13))

    def sort_table(self):
        index = self.sort_combo.currentIndex()
        if index == 0:
            self.table.sortItems(1, Qt.AscendingOrder)
        elif index == 1:
            self.table.sortItems(4, Qt.AscendingOrder)

    def filter_and_highlight_table(self):
        query = self.search_entry.text().strip().lower()
        for row in range(self.table.rowCount()):
            match_found = False
            for col in [1, 2]:
                item = self.table.item(row, col)
                if item:
                    text = item.text()
                    lower = text.lower()
                    if query and query in lower:
                        match_found = True
                        start = lower.find(query)
                        end = start + len(query)
                        highlighted = f"{text[:start]}<span style='background-color: yellow'>{text[start:end]}</span>{text[end:]}"
                        item.setData(Qt.DisplayRole, text)
                        item.setData(Qt.UserRole, highlighted)
                    else:
                        item.setData(Qt.DisplayRole, text)
                        item.setData(Qt.UserRole, text)
            self.table.setRowHidden(row, not match_found if query else False)
        self.highlight_duplicates()

    def highlight_duplicates(self):
        values = {}
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item:
                val = item.text()
                values.setdefault(val, []).append(item)

        for item_list in values.values():
            color = QColor(255, 150, 150) if len(item_list) > 1 else QColor(Qt.white)
            for item in item_list:
                item.setBackground(color)

    def add_row_to_table(self):
        munkaszam = self.entry_munkaszam.text().strip()
        megrendelo = self.entry_megrendelo.text().strip()
        if not munkaszam or not megrendelo:
            QMessageBox.warning(self, "Hiba", "A munkaszám és megrendelő nem lehet üres.")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        checkbox = QCheckBox()
        self.table.setCellWidget(row, 0, checkbox)

        values = [
            munkaszam,
            megrendelo,
            self.date_felvetel.date().toString("yyyy-MM-dd"),
            self.date_hatarido.date().toString("yyyy-MM-dd"),
            str(self.calculate_remaining_days(self.date_hatarido.date()))
        ] + ["" for _ in range(13)]

        for col, val in enumerate(values, start=1):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignCenter)
            if col == 5:
                try:
                    days = int(val)
                    if days >= 10:
                        item.setBackground(QColor("#3399ff"))
                    elif days >= 5:
                        item.setBackground(QColor("#ffffff"))
                    else:
                        item.setBackground(QColor("#ff9999"))
                except:
                    pass
            self.table.setItem(row, col, item)

        btn = QToolButton()
        btn.setText("…")
        btn.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu()
        delete_action = menu.addAction("Törlés")
        delete_action.triggered.connect(lambda _, r=row: self.delete_row(r))
        btn.setMenu(menu)
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.addWidget(btn)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 19, btn_widget)

        self.table.setItem(row, 20, QTableWidgetItem(""))

        self.save_table_data()
        self.clear_inputs()
        self.highlight_duplicates()

    def calculate_remaining_days(self, end_date):
        today = QDate.currentDate()
        days = 0
        while today < end_date:
            if today.dayOfWeek() < 6:
                days += 1
            today = today.addDays(1)
        return days

    def clear_inputs(self):
        self.entry_munkaszam.clear()
        self.entry_megrendelo.clear()
        self.date_felvetel.setDate(QDate.currentDate())
        self.date_hatarido.setDate(self.add_workdays(QDate.currentDate(), 13))

    def delete_row(self, row):
        self.table.removeRow(row)
        self.save_table_data()
        self.highlight_duplicates()

    def save_table_data(self):
        rows = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                if col == 0:
                    widget = self.table.cellWidget(row, col)
                    row_data.append(widget.isChecked() if widget else False)
                elif col == 22:
                    row_data.append("…")
                else:
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
            rows.append(row_data)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

    def load_table_data(self):
        if not os.path.exists(DATA_FILE):
            return
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            rows = json.load(f)
            for row_data in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)

                checkbox = QCheckBox()
                checkbox.setChecked(bool(row_data[0]))
                self.table.setCellWidget(row, 0, checkbox)

                for col, val in enumerate(row_data[1:19], start=1):
                    item = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)

                btn = QToolButton()
                btn.setText("…")
                btn.setPopupMode(QToolButton.InstantPopup)
                menu = QMenu()
                delete_action = menu.addAction("Törlés")
                delete_action.triggered.connect(lambda _, r=row: self.delete_row(r))
                btn.setMenu(menu)
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.addWidget(btn)
                btn_layout.setAlignment(Qt.AlignCenter)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                self.table.setCellWidget(row, 19, btn_widget)

                self.table.setItem(row, 20, QTableWidgetItem(""))
        self.highlight_duplicates()
