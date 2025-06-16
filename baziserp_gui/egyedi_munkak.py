from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QDateTimeEdit,
    QTableWidget, QTableWidgetItem, QPushButton, QGroupBox, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QLineEdit, QDateEdit, QSizePolicy, QCheckBox
)
from PyQt5.QtCore import Qt, QDate, QDateTime
from datetime import datetime, timedelta
from db import get_supabase_data
from PyQt5.QtGui import QColor
from db import update_supabase_data  # ha még nincs importálva



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

        def make_datetimeedit():
            dt = QDateTimeEdit()
            dt.setCalendarPopup(True)
            dt.setDisplayFormat("yyyy.MM.dd HH:mm")
            dt.setDateTime(QDateTime.currentDateTime())
            return dt

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
        
        checkbox_line = QHBoxLayout()
        self.eloleg_checkbox = QCheckBox("Előleg befizetve")
        self.aktiv_checkbox = QCheckBox("Aktív")
        self.aktiv_checkbox.setChecked(True)
        checkbox_line.addWidget(self.eloleg_checkbox)
        checkbox_line.addWidget(self.aktiv_checkbox)
        form_group_layout.addLayout(checkbox_line)

        self.status_combobox = QComboBox()
        self.status_dict = {}  # név → id
        status_line = QHBoxLayout()
        status_line.addWidget(QLabel("Státusz"))
        status_line.addWidget(self.status_combobox)
        form_group_layout.addLayout(status_line)

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

        self.fel_fix_input = make_datetimeedit()
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

        self.add_btn.clicked.connect(self.add_new_order)
        self.edit_btn.clicked.connect(self.edit_selected_order)

        
        # --- Alsó szakasz: sávos naptár nézet ---
        legend = QLabel("""
<b>Színmagyarázat:</b><br>
<span style='background-color:#D3D3D3;'>&nbsp;&nbsp;&nbsp;</span> Felmérés terv &nbsp;
<span style='background-color:#A9A9A9;'>&nbsp;&nbsp;&nbsp;</span> Felmérés fix &nbsp;
<span style='background-color:#FFFF00;'>&nbsp;&nbsp;&nbsp;</span> Összeszerelés terv &nbsp;
<span style='background-color:#90EE90;'>&nbsp;&nbsp;&nbsp;</span> Beszerelés terv &nbsp;
<span style='background-color:#00B050;'>&nbsp;&nbsp;&nbsp;</span> Beszerelés fix &nbsp;
<span style='background-color:#FFC000;'>&nbsp;&nbsp;&nbsp;</span> Szabászati határidő
""")
        legend_box = QGroupBox("Színmagyarázat")
        legend_layout = QVBoxLayout()
        legend_layout.addWidget(legend)
        legend_box.setLayout(legend_layout)
        layout.addWidget(legend_box)

        layout.addWidget(QLabel("Sávos naptár"))
        self.naptar_table = QTableWidget()
        self.naptar_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.naptar_table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.naptar_table.itemSelectionChanged.connect(self.limit_selection_to_single_row)


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

        self.month_header = QTableWidget()
        self.month_header.setRowCount(1)
        self.month_header.setColumnCount(self.num_days + 2)
        self.month_header.verticalHeader().hide()
        self.month_header.horizontalHeader().hide()
        self.month_header.setFixedHeight(30)
        self.month_header.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.month_header.setFocusPolicy(Qt.NoFocus)
        self.month_header.setSelectionMode(QAbstractItemView.NoSelection)
        layout.addWidget(self.month_header)


        legend.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        legend.setAlignment(Qt.AlignLeft)


        layout.addLayout(nav_layout)

        update_btn = QPushButton("Frissítés sávos nézet")
        update_btn.clicked.connect(self.update_calendar)
        layout.addWidget(update_btn)

        layout.addLayout(top_layout)
        self.setLayout(layout)
        
        self.data_table.cellClicked.connect(self.load_selected_row_data)
        self.data_table.currentCellChanged.connect(self.load_selected_row_data)
        self.refresh_table()  # ez létrehozza self.table_data-t, majd az update_calendar() is meghívható belőle
        self.load_status_options()
        self.update_calendar()

        self.naptar_table.cellClicked.connect(self.sync_table_selection)

        
        self.naptar_table.horizontalScrollBar().valueChanged.connect(
        self.month_header.horizontalScrollBar().setValue
        )
        
        
    def load_selected_row_data(self, current_row, current_column, previous_row=None, previous_column=None):
        if current_row is None or current_row < 0 or current_row >= len(self.table_data):
            return

        adat = self.table_data[current_row]

        self.name_input.setText(adat.get("megrendelo_neve", ""))
        self.munkaszam_input.setText(adat.get("munkaszam", ""))
        self.eloleg_checkbox.setChecked(adat.get("eloleg_fizetve", False))
        self.aktiv_checkbox.setChecked(adat.get("aktiv", True))

        self.date_toggle.setChecked(True)
        self.date_section.setVisible(True)

        def load_date(widget, value):
            if value:
                try:
                    d = QDate.fromString(value[:10], "yyyy-MM-dd")
                    if d.isValid():
                        widget.setDate(d)
                        return
                except:
                    pass
            widget.setDate(QDate(2000, 1, 1))

        def load_datetime(widget, value):
            if value:
                try:
                    dt = QDateTime.fromString(value[:19], "yyyy-MM-ddTHH:mm:ss")
                    if dt.isValid():
                        widget.setDateTime(dt)
                        return
                except:
                    pass
            widget.setDateTime(QDateTime.fromString("2000-01-01T00:00:00", "yyyy-MM-ddTHH:mm:ss"))

        # Dátum mezők (QDateEdit)
        load_date(self.fel_terv_tol_input, adat.get("felmeres_terv_start"))
        load_date(self.fel_terv_ig_input, adat.get("felmeres_terv_end"))
        load_date(self.szabaszati_input, adat.get("szabaszati_hatarido"))
        load_date(self.ossz_tol_input, adat.get("osszeszereles_terv_start"))
        load_date(self.ossz_ig_input, adat.get("osszeszereles_terv_end"))
        load_date(self.besz_tol_input, adat.get("beszereles_terv_start"))
        load_date(self.besz_ig_input, adat.get("beszereles_terv_end"))
        load_date(self.besz_fix_tol_input, adat.get("beszereles_fix_start"))
        load_date(self.besz_fix_ig_input, adat.get("beszereles_fix_end"))

        # Dátum+idő mező (QDateTimeEdit)
        load_datetime(self.fel_fix_input, adat.get("felmeres_fix"))
                
                # Státusz ComboBox beállítása
        statusz_id = adat.get("statusz_id")
        if statusz_id is not None:
            for nev, id_ in self.status_dict.items():
                if id_ == statusz_id:
                    self.status_combobox.setCurrentText(nev)
                    break
        else:
            self.status_combobox.setCurrentIndex(-1)

        
    
 
    def refresh_table(self):
        self.data_table.clearContents()
        self.data_table.setRowCount(0)

        headers = ["Munkaszám", "Megrendelő", "Előleg", "Státusz"]
        self.data_table.setColumnCount(len(headers))
        self.data_table.setHorizontalHeaderLabels(headers)

        params = {
            "select": "*, egyedi_megrendeles_statuszok(nev)"
        }
        if self.active_only_checkbox.isChecked():
            params["aktiv"] = "eq.true"

        data = get_supabase_data("egyedi_megrendelesek", params=params)

        if not data:
            print("Nincs adat vagy hiba történt a lekérdezés során.")
            return

        self.table_data = []

        for row_index, record in enumerate(data):
                    

            self.data_table.insertRow(row_index)
            self.table_data.append(record)

            munkaszam = str(record.get("munkaszam", ""))
            megrendelo = str(record.get("megrendelo_neve", ""))
            eloleg = "igen" if record.get("eloleg_fizetve") else "nem"
            statusz = record.get("egyedi_megrendeles_statuszok", {}).get("nev", "")

            munkaszam_item = QTableWidgetItem(munkaszam)
            megrendelo_item = QTableWidgetItem(megrendelo)
            eloleg_item = QTableWidgetItem(eloleg)
            statusz_item = QTableWidgetItem(statusz)

            if not record.get("aktiv", True):
                inactive_color = QColor(220, 220, 220)
                munkaszam_item.setBackground(inactive_color)
                megrendelo_item.setBackground(inactive_color)
                eloleg_item.setBackground(inactive_color)
                statusz_item.setBackground(inactive_color)

            if record.get("eloleg_fizetve") is True:
                eloleg_item.setBackground(QColor(200, 255, 200))

            self.data_table.setItem(row_index, 0, munkaszam_item)
            self.data_table.setItem(row_index, 1, megrendelo_item)
            self.data_table.setItem(row_index, 2, eloleg_item)
            self.data_table.setItem(row_index, 3, statusz_item)

        self.data_table.repaint()
        
        print("Betöltött rekordok száma:", len(self.table_data))

    def jump_to_today(self):
        self.start_date = self.today
        self.update_calendar()

    def jump_to_date(self):  # <--- ezt add hozzá
        d = self.date_input.date().toPyDate()
        self.start_date = datetime(d.year, d.month, d.day)
        self.update_calendar()

    def color_range(self, row, date_from_str, date_to_str, hex_color):
        try:
            if not date_from_str or date_from_str.startswith("2000-01-01"):
                return
            start = datetime.strptime(date_from_str[:10], "%Y-%m-%d")
            if not date_to_str or date_to_str.startswith("2000-01-01"):
                end = start
            else:
                end = datetime.strptime(date_to_str[:10], "%Y-%m-%d")
        except Exception as e:
            print("Hibás dátumformátum a color_range-ben:", e)
            return

        for i in range((end - start).days + 1):
            day = start + timedelta(days=i)
            col = (day - self.start_date).days + 3
            if 2 <= col < self.naptar_table.columnCount():
                cell = QTableWidgetItem()
                cell.setBackground(QColor(hex_color))
                self.naptar_table.setItem(row, col, cell)


    def update_calendar(self):
        self.naptar_table.clear()
        
        self.month_header.clear()
        col = 2  # első két oszlop a munkaszám és megrendelő

        current_month = ""
        month_start_col = col

        for i in range(self.num_days):
            date = self.start_date + timedelta(days=i)
            month_name = date.strftime("%B")

            if month_name != current_month:
                if current_month != "":
                    span = col - month_start_col
                    self.month_header.setSpan(0, month_start_col, 1, span)
                    item = QTableWidgetItem(current_month)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.month_header.setItem(0, month_start_col, item)
                current_month = month_name
                month_start_col = col
            col += 1

        # utolsó hónap befejezése
        span = col - month_start_col
        self.month_header.setSpan(0, month_start_col, 1, span)
        item = QTableWidgetItem(current_month)
        item.setTextAlignment(Qt.AlignCenter)
        self.month_header.setItem(0, month_start_col, item)

        # resize sync
        self.month_header.setColumnWidth(0, self.naptar_table.columnWidth(0))
        self.month_header.setColumnWidth(1, self.naptar_table.columnWidth(1))
        for i in range(2, self.num_days + 2):
            self.month_header.setColumnWidth(i, self.naptar_table.columnWidth(i))

        
        rows = len(self.table_data)
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
            if date.weekday() in (5, 6):  # hétvége
                item = self.naptar_table.horizontalHeaderItem(i + 2)
                if item:
                    item.setForeground(QColor("red"))

        for row, adat in enumerate(self.table_data):
            self.naptar_table.setItem(row, 0, QTableWidgetItem(adat.get("munkaszam", "")))
            self.naptar_table.setItem(row, 1, QTableWidgetItem(adat.get("megrendelo_neve", "")))

            self.color_range(row, adat.get("felmeres_terv_start"), adat.get("felmeres_terv_end"), "#D3D3D3")
            self.color_range(row, adat.get("felmeres_fix"), adat.get("felmeres_fix"), "#A9A9A9")
            self.color_range(row, adat.get("osszeszereles_terv_start"), adat.get("osszeszereles_terv_end"), "#FFFF00")
            self.color_range(row, adat.get("beszereles_terv_start"), adat.get("beszereles_terv_end"), "#90EE90")
            self.color_range(row, adat.get("beszereles_fix_start"), adat.get("beszereles_fix_end"), "#00B050")

            # Szabászati határidő: osszeszereles_terv_start - 1 nap
            self.color_range(row, adat.get("szabaszati_hatarido"), adat.get("szabaszati_hatarido"), "#FFC000")


        # mai nap kiemelése
        if today_col:
            for row in range(rows):
                item = self.naptar_table.item(row, today_col)
                if item is None:
                    item = QTableWidgetItem()
                    self.naptar_table.setItem(row, today_col, item)
                
                current_color = item.background().color()
                if current_color == QColor(Qt.white) or not item.background().isOpaque():
                    item.setBackground(QColor("#FFEFD5"))  # halványsárga kiemelés


        self.naptar_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.naptar_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        print("update_calendar() meghívva")

        print("Debug table_data:", self.table_data)


    
    def add_new_order(self):
        adat = self.collect_form_data()
        if not adat:
            return

        from db import insert_supabase_data  # csak ha nem importáltad

        response = insert_supabase_data("egyedi_megrendelesek", adat)
        if response:
            QMessageBox.information(self, "Siker", "Új megrendelés hozzáadva.")
            self.refresh_table()
        else:
            QMessageBox.critical(self, "Hiba", "Nem sikerült a mentés.")

    def edit_selected_order(self):
        row = self.data_table.currentRow()
        if row < 0 or row >= len(self.table_data):
            QMessageBox.warning(self, "Figyelem", "Nincs kiválasztott sor.")
            return

        record_id = self.table_data[row].get("id")
        if not record_id:
            QMessageBox.critical(self, "Hiba", "Nem található az azonosító.")
            return

        def date_or_none(widget):
            d = widget.date()
            if d == QDate(2000, 1, 1):
                return None
            return d.toString("yyyy-MM-dd")

        def datetime_or_none(widget):
            d = widget.dateTime()
            if d.date() == QDate(2000, 1, 1):
                return None
            return d.toString("yyyy-MM-ddThh:mm:ss")

        data = {
            "megrendelo_neve": self.name_input.text().strip(),
            "munkaszam": self.munkaszam_input.text().strip(),
            "eloleg_fizetve": self.eloleg_checkbox.isChecked(),
            "aktiv": self.aktiv_checkbox.isChecked(),
            "felmeres_terv_start": date_or_none(self.fel_terv_tol_input),
            "felmeres_terv_end": date_or_none(self.fel_terv_ig_input),
            "felmeres_fix": datetime_or_none(self.fel_fix_input),
            "szabaszati_hatarido": date_or_none(self.szabaszati_input),
            "osszeszereles_terv_start": date_or_none(self.ossz_tol_input),
            "osszeszereles_terv_end": date_or_none(self.ossz_ig_input),
            "beszereles_terv_start": date_or_none(self.besz_tol_input),
            "beszereles_terv_end": date_or_none(self.besz_ig_input),
            "beszereles_fix_start": date_or_none(self.besz_fix_tol_input),
            "beszereles_fix_end": date_or_none(self.besz_fix_ig_input),
        }

        # Státusz ID hozzárendelés a ComboBox-ból
        status_text = self.status_combobox.currentText()
        status_id = self.status_dict.get(status_text)
        if status_id:
            data["statusz_id"] = status_id

        print("Frissítendő rekord ID:", record_id)
        print("Adat:", data)

        success = update_supabase_data("egyedi_megrendelesek", record_id, data)
        if success:
            QMessageBox.information(self, "Siker", "Sikeresen frissítve.")
            self.refresh_table()
        else:
            QMessageBox.critical(self, "Hiba", "Nem sikerült frissíteni a rekordot.")
    
    

    def collect_form_data(self):
        megrendelo = self.name_input.text().strip()
        munkaszam = self.munkaszam_input.text().strip()
        if not megrendelo or not munkaszam:
            QMessageBox.warning(self, "Hiányzó adatok", "A megrendelő neve és a munkaszám kötelező.")
            return None

        adat = {
            "megrendelo_neve": megrendelo,
            "munkaszam": munkaszam,
            "eloleg_fizetve": self.eloleg_checkbox.isChecked(),
            "aktiv": self.aktiv_checkbox.isChecked(),
            "felmeres_terv_tol": self.fel_terv_tol_input.date().toString("yyyy-MM-dd"),
            "felmeres_terv_ig": self.fel_terv_ig_input.date().toString("yyyy-MM-dd"),
            "felmeres_fix": self.fel_fix_input.dateTime().toString(Qt.ISODate),
            "szabaszati_hatarido": self.szabaszati_input.date().toString("yyyy-MM-dd"),
            "osszeszereles_terv_tol": self.ossz_tol_input.date().toString("yyyy-MM-dd"),
            "osszeszereles_terv_ig": self.ossz_ig_input.date().toString("yyyy-MM-dd"),
            "beszereles_terv_tol": self.besz_tol_input.date().toString("yyyy-MM-dd"),
            "beszereles_terv_ig": self.besz_ig_input.date().toString("yyyy-MM-dd"),
            "beszereles_fix_tol": self.besz_fix_tol_input.date().toString("yyyy-MM-dd"),
            "beszereles_fix_ig": self.besz_fix_ig_input.date().toString("yyyy-MM-dd")
        }

        return adat

    def load_status_options(self):
        from db import get_supabase_data
        statuszok = get_supabase_data("egyedi_megrendeles_statuszok")
        self.status_combobox.clear()
        self.status_dict = {}

        for rekord in statuszok:
            nev = rekord.get("nev", "ismeretlen")
            id_ = rekord.get("id")
            self.status_dict[nev] = id_
            self.status_combobox.addItem(nev)

        self.status_combobox.setCurrentIndex(-1)

    def shift_days(self, offset):
        self.start_date += timedelta(days=offset)
        new_qdate = QDate(self.start_date.year, self.start_date.month, self.start_date.day)
        self.date_input.setDate(new_qdate)
        self.update_calendar()

    def sync_table_selection(self, row, column):
        self.data_table.selectRow(row)
        self.data_table.scrollToItem(self.data_table.item(row, 0))

    def limit_selection_to_row(self):
        selected_indexes = self.naptar_table.selectedIndexes()
        if not selected_indexes:
            return

        rows = {index.row() for index in selected_indexes}
        if len(rows) > 1:
            # Ha több sorba is kijelöltek, visszaállítjuk csak az első sort
            target_row = selected_indexes[0].row()
            cols = [index.column() for index in selected_indexes if index.row() == target_row]

            self.naptar_table.clearSelection()
            for col in cols:
                self.naptar_table.item(target_row, col).setSelected(True)

    def limit_selection_to_single_row(self):
        selected_indexes = self.naptar_table.selectedIndexes()
        if not selected_indexes:
            return

        first_row = selected_indexes[0].row()
        filtered = [index for index in selected_indexes if index.row() == first_row]

        if len(filtered) < len(selected_indexes):
            self.naptar_table.blockSignals(True)
            self.naptar_table.clearSelection()
            for index in filtered:
                item = self.naptar_table.item(index.row(), index.column())
                if item is None:
                    item = QTableWidgetItem()
                    self.naptar_table.setItem(index.row(), index.column(), item)
                item.setSelected(True)
            self.naptar_table.blockSignals(False)
