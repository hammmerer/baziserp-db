from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QAbstractItemView, QFrame, QLineEdit, QDateEdit, QSizePolicy)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush
from datetime import datetime, timedelta
import random


class EgyediMunkakTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.munkak = []
        self.today = datetime.today()
        self.start_date = self.today
        self.num_days = 40

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # bal–jobb layout kialakítása
        top_layout = QHBoxLayout()

        # Táblázat bal oldalon – csak 2 oszlop
        self.data_table = QTableWidget(0, 2)
        self.data_table.setHorizontalHeaderLabels(["Munkaszám", "Megrendelő"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_table.itemSelectionChanged.connect(self.on_row_selected)
        top_layout.addWidget(self.data_table, 1)
        
        # Jobb oldal: beviteli mezők és gombok
        form_layout = QVBoxLayout()

        self.fel_terv_input = QLineEdit()
        self.fel_fix_input = QLineEdit()
        self.ossz_input = QLineEdit()
        self.besz_input = QLineEdit()
        self.besz_fix_input = QLineEdit()

        form_layout.addWidget(QLabel("Felmérés terv"))
        form_layout.addWidget(self.fel_terv_input)
        form_layout.addWidget(QLabel("Felmérés fix"))
        form_layout.addWidget(self.fel_fix_input)
        form_layout.addWidget(QLabel("Összeszerelés terv"))
        form_layout.addWidget(self.ossz_input)
        form_layout.addWidget(QLabel("Beszerelés terv"))
        form_layout.addWidget(self.besz_input)
        form_layout.addWidget(QLabel("Beszerelés fix"))
        form_layout.addWidget(self.besz_fix_input)

        # Gombok
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Új hozzáadása")
        self.edit_btn = QPushButton("Módosítás")
        self.delete_btn = QPushButton("Törlés")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)

        form_layout.addLayout(btn_layout)
        top_layout.addLayout(form_layout, 2)


        self.example_data = [
            ["E142", "Kiss János", "06.17–06.21", "06.18", "07.01–07.03", "07.04–07.08", "07.06–07.07"],
            ["E143", "Nagy Béla", "06.12–06.13", "06.13", "06.20–06.22", "06.25–06.27", "06.26–06.27"],
            ["E144", "Szabó Éva", "06.20–06.22", "06.21", "07.05–07.07", "07.08–07.10", "07.09–07.10"]
        ]

        for i in range(15):
            munkaszam = f"E{145 + i}"
            nev = f"Teszt Megrendelő {i+1}"
            base = datetime(2025, 6, 10) + timedelta(days=random.randint(0, 90))
            fel_terv = base.strftime("%m.%d") + "–" + (base + timedelta(days=2)).strftime("%m.%d")
            fel_fix = (base + timedelta(days=1)).strftime("%m.%d")
            ossz = (base + timedelta(days=10)).strftime("%m.%d") + "–" + (base + timedelta(days=12)).strftime("%m.%d")
            besz = (base + timedelta(days=13)).strftime("%m.%d") + "–" + (base + timedelta(days=15)).strftime("%m.%d")
            besz_fix = (base + timedelta(days=14)).strftime("%m.%d") + "–" + (base + timedelta(days=15)).strftime("%m.%d")
            self.example_data.append([munkaszam, nev, fel_terv, fel_fix, ossz, besz, besz_fix])

        for row, sor in enumerate(self.example_data):
            for col, value in enumerate(sor):
                self.data_table.setItem(row, col, QTableWidgetItem(value))

        layout.addWidget(QLabel("Munkák listája"))
        layout.addLayout(top_layout)

        legend = QLabel("""
<b>Színmagyarázat:</b><br>
<span style='background-color:#D3D3D3;'>&nbsp;&nbsp;&nbsp;</span> Felmérés terv &nbsp;
<span style='background-color:#A9A9A9;'>&nbsp;&nbsp;&nbsp;</span> Felmérés fix &nbsp;
<span style='background-color:#FFFF00;'>&nbsp;&nbsp;&nbsp;</span> Összeszerelés terv &nbsp;
<span style='background-color:#90EE90;'>&nbsp;&nbsp;&nbsp;</span> Beszerelés terv &nbsp;
<span style='background-color:#00B050;'>&nbsp;&nbsp;&nbsp;</span> Beszerelés fix &nbsp;
<span style='background-color:#FFC000;'>&nbsp;&nbsp;&nbsp;</span> Szabászati határidő
""")
        legend.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        legend.setAlignment(Qt.AlignLeft)
        layout.addWidget(legend)

        self.naptar_table = QTableWidget()
        layout.addWidget(QLabel("Sávos naptár"))
        layout.addWidget(self.naptar_table)

        nav_layout = QHBoxLayout()
        nav_layout.setAlignment(Qt.AlignCenter)

        for label, days in [("<30", -30), ("<15", -15), ("<7", -7)]:
            btn = QPushButton(label)
            btn.setFixedWidth(40)
            btn.clicked.connect(lambda _, d=days: self.shift_days(d))
            nav_layout.addWidget(btn)

        nav_layout.addWidget(QLabel("Ugrás dátumra:"))
        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("yy.MM.dd")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setFixedWidth(150)
        nav_layout.addWidget(self.date_input)

        go_btn = QPushButton("Ugrás")
        go_btn.setFixedWidth(50)
        go_btn.clicked.connect(self.jump_to_date)
        nav_layout.addWidget(go_btn)

        ma_btn = QPushButton("MA")
        ma_btn.setFixedWidth(40)
        ma_btn.clicked.connect(self.jump_to_today)
        nav_layout.addWidget(ma_btn)

        for label, days in [("7>", 7), ("15>", 15), ("30>", 30)]:
            btn = QPushButton(label)
            btn.setFixedWidth(40)
            btn.clicked.connect(lambda _, d=days: self.shift_days(d))
            nav_layout.addWidget(btn)

        layout.addLayout(nav_layout)

        update_btn = QPushButton("Frissítés sávos nézet")
        update_btn.clicked.connect(self.update_calendar)
        layout.addWidget(update_btn)

        self.setLayout(layout)
        self.add_btn.clicked.connect(self.add_row)
        self.edit_btn.clicked.connect(self.edit_row)
        self.delete_btn.clicked.connect(self.delete_row)
        self.refresh_table()
        
        self.update_calendar()

    def shift_days(self, days):
        self.start_date += timedelta(days=days)
        self.update_calendar()

    def jump_to_date(self):
        d = self.date_input.date().toPyDate()
        self.start_date = datetime(d.year, d.month, d.day)
        self.update_calendar()

    def jump_to_today(self):
        self.start_date = self.today
        self.update_calendar()

    def update_calendar(self):
        self.naptar_table.clear()

        rows = len(self.example_data)
        cols = self.num_days + 2
        self.naptar_table.setRowCount(rows)
        self.naptar_table.setColumnCount(cols)

        headers = ["Munkaszám", "Megrendelő"]
        today_col = None
        for i in range(self.num_days):
            date = self.start_date + timedelta(days=i)
            headers.append(date.strftime("%d"))
            if date.date() == self.today.date():
                today_col = i + 2
        self.naptar_table.setHorizontalHeaderLabels(headers)

        for i in range(self.num_days):
            date = self.start_date + timedelta(days=i)
            if date.weekday() in (5, 6):  # szombat, vasárnap
                item = self.naptar_table.horizontalHeaderItem(i + 2)
                if item:
                    item.setForeground(QBrush(QColor("red")))

        for row in range(rows):
            adat = self.example_data[row]
            self.naptar_table.setItem(row, 0, QTableWidgetItem(adat[0]))  # Munkaszám
            self.naptar_table.setItem(row, 1, QTableWidgetItem(adat[1]))  # Megrendelő

            self.color_range(row, adat[2], "#D3D3D3")   # Felmérés terv
            self.color_range(row, adat[3], "#A9A9A9")   # Felmérés fix
            self.color_range(row, adat[4], "#FFFF00")   # Összeszerelés terv
            self.color_range(row, adat[5], "#90EE90")   # Beszerelés terv
            self.color_range(row, adat[6], "#00B050")   # Beszerelés fix

            # Szabászati határidő – 1 nappal az összeszerelés előtt
            ossz = self.get_date_range_text(adat[4])
            if ossz:
                szab_datum = ossz[0] - timedelta(days=1)
                index = (szab_datum - self.start_date).days + 2
                if 2 <= index < self.naptar_table.columnCount():
                    item = QTableWidgetItem()
                    item.setBackground(QColor("#FFC000"))
                    self.naptar_table.setItem(row, index, item)

        # mai nap kiemelése
        if today_col:
            for row in range(rows):
                item = self.naptar_table.item(row, today_col)
                if not item:
                    item = QTableWidgetItem()
                    self.naptar_table.setItem(row, today_col, item)
                item.setBackground(QColor("#FFEFD5"))  # halvány sárga kiemelés

        self.naptar_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.naptar_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def color_phase(self, row, data_col, hex_color):
        item = self.data_table.item(row, data_col)
        if not item:
            return
        dates = self.get_date_range(item)
        if not dates:
            return
        start, end = dates
        for i in range((end - start).days + 1):
            day = start + timedelta(days=i)
            col = (day - self.start_date).days + 2
            if 2 <= col < self.naptar_table.columnCount():
                cell = QTableWidgetItem()
                cell.setBackground(QColor(hex_color))
                self.naptar_table.setItem(row, col, cell)

    def get_date_range(self, item):
        try:
            text = item.text().strip()
            if "–" in text:
                d1, d2 = text.split("–")
                y = self.start_date.year
                start = datetime.strptime(d1.strip(), "%m.%d").replace(year=y)
                end = datetime.strptime(d2.strip(), "%m.%d").replace(year=y)
                return (start, end)
            else:
                d = datetime.strptime(text.strip(), "%m.%d").replace(year=self.start_date.year)
                return (d, d)
        except:
            return None

    def on_row_selected(self):
        selected = self.data_table.currentRow()
        if selected >= 0 and selected < len(self.example_data):
            adat = self.example_data[selected]
            self.fel_terv_input.setText(adat[2])
            self.fel_fix_input.setText(adat[3])
            self.ossz_input.setText(adat[4])
            self.besz_input.setText(adat[5])
            self.besz_fix_input.setText(adat[6])

            # kijelölés az alsó táblában
            self.naptar_table.selectRow(selected)
            self.naptar_table.scrollToItem(self.naptar_table.item(selected, 0), QAbstractItemView.PositionAtCenter)


    def add_row(self):
        new_id = f"E{142 + len(self.example_data)}"
        new_name = f"Új Megrendelő {len(self.example_data) + 1}"
        new_data = [
            new_id,
            new_name,
            self.fel_terv_input.text(),
            self.fel_fix_input.text(),
            self.ossz_input.text(),
            self.besz_input.text(),
            self.besz_fix_input.text()
        ]
        self.example_data.append(new_data)
        self.refresh_table()


    def edit_row(self):
        selected = self.data_table.currentRow()
        if selected >= 0 and selected < len(self.example_data):
            self.example_data[selected][2] = self.fel_terv_input.text()
            self.example_data[selected][3] = self.fel_fix_input.text()
            self.example_data[selected][4] = self.ossz_input.text()
            self.example_data[selected][5] = self.besz_input.text()
            self.example_data[selected][6] = self.besz_fix_input.text()

    def delete_row(self):
        selected = self.data_table.currentRow()
        if selected >= 0 and selected < len(self.example_data):
            self.example_data.pop(selected)
            self.refresh_table()

    def refresh_table(self):
        self.data_table.setRowCount(0)
        for row_idx, row_data in enumerate(self.example_data):
            self.data_table.insertRow(row_idx)
            self.data_table.setItem(row_idx, 0, QTableWidgetItem(row_data[0]))  # Munkaszám
            self.data_table.setItem(row_idx, 1, QTableWidgetItem(row_data[1]))  # Megrendelő

    def on_row_selected(self):
        selected = self.data_table.currentRow()
        if selected >= 0 and selected < len(self.example_data):
            adat = self.example_data[selected]
            self.fel_terv_input.setText(adat[2])
            self.fel_fix_input.setText(adat[3])
            self.ossz_input.setText(adat[4])
            self.besz_input.setText(adat[5])
            self.besz_fix_input.setText(adat[6])
            
    def get_date_range_text(self, text):
        try:
            if "–" in text:
                d1, d2 = text.split("–")
                y = self.start_date.year
                start = datetime.strptime(d1.strip(), "%m.%d").replace(year=y)
                end = datetime.strptime(d2.strip(), "%m.%d").replace(year=y)
                return (start, end)
            else:
                d = datetime.strptime(text.strip(), "%m.%d").replace(year=self.start_date.year)
                return (d, d)
        except:
            return None

    def color_range(self, row, text, hex_color):
        dates = self.get_date_range_text(text)
        if not dates:
            return
        start, end = dates
        for i in range((end - start).days + 1):
            day = start + timedelta(days=i)
            col = (day - self.start_date).days + 2
            if 2 <= col < self.naptar_table.columnCount():
                cell = QTableWidgetItem()
                cell.setBackground(QColor(hex_color))
                self.naptar_table.setItem(row, col, cell)
