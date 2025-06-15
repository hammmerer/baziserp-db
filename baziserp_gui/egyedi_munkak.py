from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox,
    QTableWidget, QTableWidgetItem, QPushButton, QGroupBox,
    QHeaderView, QAbstractItemView, QFrame, QLineEdit, QDateEdit, QSizePolicy, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from db import get_supabase_data

class EgyediMunkakTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.today = datetime.today()
        self.start_date = self.today
        self.num_days = 40

        self.init_ui()
        self.refresh_table()

    def init_ui(self):

        def make_dateedit():
            d = QDateEdit()
            d.setCalendarPopup(True)
            d.setDisplayFormat("yyyy.MM.dd")
            d.setSpecialValueText("")
            d.setDate(QDate(2000, 1, 1))
            d.setMinimumDate(QDate(1752, 9, 14))
            d.calendarWidget().activated.connect(
                lambda date: d.setDate(QDate.currentDate()) if d.date() == QDate(2000, 1, 1) else None
            )
            return d

        layout = QVBoxLayout(self)

        self.active_only_checkbox = QCheckBox("Csak az aktív munkák mutatása")
        self.active_only_checkbox.setChecked(True)
        self.active_only_checkbox.stateChanged.connect(self.refresh_table)
        layout.addWidget(self.active_only_checkbox)

        top_layout = QHBoxLayout()
        form_layout = QVBoxLayout()

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["Munkaszám", "Megrendelő", "Előleg"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_table.setSortingEnabled(True)
        top_layout.addWidget(self.data_table, 1)

        form_group = QGroupBox("Megrendelés adatai")
        form_group_layout = QVBoxLayout()

        line1 = QHBoxLayout()
        self.name_input = QLineEdit()
        self.munkaszam_input = QLineEdit()
        line1.addWidget(QLabel("Megrendelő neve"))
        line1.addWidget(self.name_input)
        line1.addWidget(QLabel("Munkaszám"))
        line1.addWidget(self.munkaszam_input)
        form_group_layout.addLayout(line1)

        self.date_toggle = QCheckBox("Dátumok megadása")
        self.date_toggle.setChecked(False)
        form_group_layout.addWidget(self.date_toggle)

        self.date_section = QWidget()
        date_section_layout = QVBoxLayout(self.date_section)

        self.fel_terv_tol_input = make_dateedit()
        self.fel_terv_ig_input = make_dateedit()
        line2 = QHBoxLayout()
        line2.addWidget(QLabel("Felmérés terv – tól"))
        line2.addWidget(self.fel_terv_tol_input)
        line2.addWidget(QLabel("– ig"))
        line2.addWidget(self.fel_terv_ig_input)
        date_section_layout.addLayout(line2)

        self.fel_fix_input = make_dateedit()
        line3 = QHBoxLayout()
        line3.addWidget(QLabel("Felmérés fix"))
        line3.addWidget(self.fel_fix_input)
        date_section_layout.addLayout(line3)

        self.szabaszati_input = make_dateedit()
        line4 = QHBoxLayout()
        line4.addWidget(QLabel("Szabászati határidő"))
        line4.addWidget(self.szabaszati_input)
        date_section_layout.addLayout(line4)

        self.ossz_tol_input = make_dateedit()
        self.ossz_ig_input = make_dateedit()
        line5 = QHBoxLayout()
        line5.addWidget(QLabel("Összeszerelés terv – tól"))
        line5.addWidget(self.ossz_tol_input)
        line5.addWidget(QLabel("– ig"))
        line5.addWidget(self.ossz_ig_input)
        date_section_layout.addLayout(line5)

        self.besz_tol_input = make_dateedit()
        self.besz_ig_input = make_dateedit()
        line6 = QHBoxLayout()
        line6.addWidget(QLabel("Beszerelés terv – tól"))
        line6.addWidget(self.besz_tol_input)
        line6.addWidget(QLabel("– ig"))
        line6.addWidget(self.besz_ig_input)
        date_section_layout.addLayout(line6)

        self.besz_fix_tol_input = make_dateedit()
        self.besz_fix_ig_input = make_dateedit()
        line7 = QHBoxLayout()
        line7.addWidget(QLabel("Beszerelés fix – tól"))
        line7.addWidget(self.besz_fix_tol_input)
        line7.addWidget(QLabel("– ig"))
        line7.addWidget(self.besz_fix_ig_input)
        date_section_layout.addLayout(line7)

        self.date_section.setVisible(False)
        self.date_toggle.stateChanged.connect(lambda state: self.date_section.setVisible(state == Qt.Checked))
        form_group_layout.addWidget(self.date_section)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Új hozzáadása")
        self.edit_btn = QPushButton("Módosítás")
        self.delete_btn = QPushButton("Törlés")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        form_group_layout.addStretch()
        form_group_layout.addLayout(btn_layout)

        form_group.setLayout(form_group_layout)
        form_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout.addWidget(form_group)
        top_layout.addLayout(form_layout, 2)

        layout.addLayout(top_layout)
        self.setLayout(layout)

        self.data_table.cellClicked.connect(self.load_selected_row_data)
        self.data_table.currentCellChanged.connect(self.load_selected_row_data)

    def refresh_table(self):
        self.data_table.clearContents()
        self.data_table.setRowCount(0)

        headers = ["Munkaszám", "Megrendelő", "Előleg"]
        keys = ["munkaszam", "megrendelo_neve", "eloleg_fizetve"]

        self.data_table.setColumnCount(len(headers))
        self.data_table.setHorizontalHeaderLabels(headers)

        if self.active_only_checkbox.isChecked():
            data = get_supabase_data("egyedi_megrendelesek", params={"aktiv": "eq.true"})
        else:
            data = get_supabase_data("egyedi_megrendelesek")

        if not data:
            print("Nincs adat vagy hiba történt a lekérdezés során.")
            return

        self.table_data = []

        for row_index, record in enumerate(data):
            self.data_table.insertRow(row_index)
            self.table_data.append(record)

            for col_index, key in enumerate(keys):
                value = "igen" if record.get(key) is True else ("nem" if record.get(key) is False else str(record.get(key, "")))
                self.data_table.setItem(row_index, col_index, QTableWidgetItem(value))

        self.data_table.repaint()
    def load_selected_row_data(self, current_row, current_column, previous_row=None, previous_column=None):
        if current_row is None or current_row < 0 or current_row >= len(self.table_data):
            return

        adat = self.table_data[current_row]
        # további mezők kitöltése itt...



        self.name_input.setText(adat.get("megrendelo_neve", ""))
        self.munkaszam_input.setText(adat.get("munkaszam", ""))

        self.date_toggle.setChecked(True)
        self.date_section.setVisible(True)

        def set_date_safe(widget, key):
            val = adat.get(key)
            if val:
                try:
                    d = QDate.fromString(val[:10], "yyyy-MM-dd")
                    if d.isValid():
                        widget.setDate(d)
                except:
                    pass

        set_date_safe(self.fel_terv_tol_input, "felmeres_terv_tol")
        set_date_safe(self.fel_terv_ig_input, "felmeres_terv_ig")
        set_date_safe(self.fel_fix_input, "felmeres_fix")
        set_date_safe(self.szabaszati_input, "szabaszati_hatarido")
        set_date_safe(self.ossz_tol_input, "osszeszereles_terv_tol")
        set_date_safe(self.ossz_ig_input, "osszeszereles_terv_ig")
        set_date_safe(self.besz_tol_input, "beszereles_terv_tol")
        set_date_safe(self.besz_ig_input, "beszereles_terv_ig")
        set_date_safe(self.besz_fix_tol_input, "beszereles_fix_tol")
        set_date_safe(self.besz_fix_ig_input, "beszereles_fix_ig")