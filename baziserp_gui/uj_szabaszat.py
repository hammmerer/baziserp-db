from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QRadioButton, QCheckBox,
    QSizePolicy, QGridLayout, QSpacerItem, QHeaderView, QSplitter, QButtonGroup, QComboBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QEvent, QPoint, QTimer
import pandas as pd

class UjMegrendelesTab(QWidget):
    def __init__(self):
        super().__init__()

        try:
            df = pd.read_excel("baziserp_gui/anyaglista.xlsx")
            self.anyag_lista = df["megnevezés"].dropna().tolist()
        except Exception as e:
            print("Nem sikerült betölteni az anyaglistát:", e)
            self.anyag_lista = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)

       # Új felső szakasz két oszlopos elrendezéssel (anyaglista + információs mezők)
        upper_container = QWidget()
        upper_container_layout = QHBoxLayout(upper_container)
        upper_container_layout.setContentsMargins(0, 0, 0, 0)
        upper_container_layout.setSpacing(20)

        # Bal oldali rész: Anyagok Listája
        upper_left_layout = QVBoxLayout()
        upper_left_layout.setContentsMargins(0, 0, 0, 0)
        upper_left_layout.setSpacing(5)

        elerheto_label = QLabel("Anyagok Listája")
        elerheto_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px")
        upper_left_layout.addWidget(elerheto_label)

        self.anyagok_table = QTableWidget()
        self.anyagok_table.setColumnCount(4)
        self.anyagok_table.setHorizontalHeaderLabels(["", "Lista név", "Anyag", "Dátum/Idő"])
        self.anyagok_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.anyagok_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.select_all_checkbox = QCheckBox()
        self.select_all_checkbox.setTristate(False)
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_anyagok_checkboxes)
        self.anyagok_table.setCellWidget(0, 0, self.select_all_checkbox)

        upper_left_layout.addWidget(self.anyagok_table)

        # Jobb oldali információs blokk
        info_box = QGroupBox("Anyag információk")
        info_layout = QVBoxLayout(info_box)
        info_layout.setSpacing(6)

        anyag_label = QLabel("Anyag")
        # Anyag input mező
        self.anyag_input = QLineEdit()
        anyag_layout = QVBoxLayout()
        anyag_layout.addWidget(QLabel("Anyag"))
        anyag_layout.addWidget(self.anyag_input)


       
        self.anyag_suggestions = QListWidget(self)
        self.anyag_suggestions.setWindowFlags(Qt.Popup)
        self.anyag_suggestions.setFocusPolicy(Qt.NoFocus)
        self.anyag_suggestions.setMouseTracking(True)
        self.anyag_suggestions.setVisible(False)
        self.anyag_suggestions.installEventFilter(self)

        self.anyag_suggestions.itemClicked.connect(self.select_suggestion)
        self.anyag_input.textChanged.connect(self.filter_anyagok)
        self.anyag_input.installEventFilter(self)

        # Eseményfigyelő (csak ezután lehet hívni!)

        info_layout.addLayout(anyag_layout)

        elzaro_label = QLabel("Élzárók")
        elzaro_label.setStyleSheet("font-weight: bold; padding-top: 10px")
        info_layout.addWidget(elzaro_label)

        self.elzaro_inputs = []

        for i in range(1, 7):
            row = QHBoxLayout()
            row.setSpacing(5)
            row.addWidget(QLabel(f"{i}."))
            
            input1 = QLineEdit()
            input1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            if i >= 5:
                input2 = QLineEdit()
                input2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                row.addWidget(input1)
                row.addWidget(input2)
                self.elzaro_inputs.append((input1, input2))
            else:
                row.addWidget(input1)
                self.elzaro_inputs.append(input1)

            info_layout.addLayout(row)

        # Elrendezés beállítása: 2/3 – 1/3
        upper_container_layout.addLayout(upper_left_layout, 2)
        upper_container_layout.addWidget(info_box, 1)

        # A `upper_container`-t adjuk hozzá a splitterhez az eredeti `upper_widget` helyett
        splitter.addWidget(upper_container)
        splitter.setStretchFactor(0, 1)


        # Alsó rész - szabáslista
        lower_widget = QWidget()
        lower_layout = QVBoxLayout(lower_widget)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        lower_layout.setSpacing(5)

        self.lista_info = QLabel("Szabáslista")
        self.lista_info.setStyleSheet("font-weight: bold; padding: 5px")
        lower_layout.addWidget(self.lista_info)

        self.lista_table = QTableWidget()
        self.lista_table.setColumnCount(11)
        self.lista_table.setHorizontalHeaderLabels([
            "", "#", "Szálirány", "Keresztirány", "db.", "Élzárás", "Forg.", "Munkaszám", "Név", "Elem", "Megjegyzés"
        ])
        self.lista_table.horizontalHeader().setStretchLastSection(True)
        self.lista_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lower_layout.addWidget(self.lista_table)

        spacer = QSpacerItem(0, 20)
        lower_layout.addItem(spacer)

        buttons_wrapper = QWidget()
        buttons_layout = QHBoxLayout(buttons_wrapper)
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignLeft)

        for text in [
            "Lista törlése",
            "Kijelölt elem(ek) törlése",
            "Forgathatóság",
            "A kijelölt elemek méreteinek felcserélése",
            "Azonos sorok összevonása",
            "Sor szétbontása/duplikálása"
        ]:
            button = QPushButton(text)
            button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            buttons_layout.addWidget(button)

        lower_layout.addWidget(buttons_wrapper)

        bottom_row_wrapper = QWidget()
        bottom_row_layout = QHBoxLayout(bottom_row_wrapper)
        bottom_row_layout.setSpacing(20)
        bottom_row_layout.setAlignment(Qt.AlignLeft)

        meretek_group = QGroupBox("- Méretek megadása")
        input_grid = QGridLayout(meretek_group)
        input_grid.setHorizontalSpacing(10)
        input_grid.setVerticalSpacing(4)
        input_grid.setAlignment(Qt.AlignLeft)
        input_grid.setAlignment(Qt.AlignTop)

        input_grid.addWidget(QLabel("Szálirány"), 0, 0)
        self.szali_input = QLineEdit()
        self.szali_input.setFixedWidth(60)
        input_grid.addWidget(self.szali_input, 1, 0)

        input_grid.addWidget(QLabel("Keresztirány"), 0, 1)
        self.kereszt_input = QLineEdit()
        self.kereszt_input.setFixedWidth(60)
        input_grid.addWidget(self.kereszt_input, 1, 1)

        input_grid.addWidget(QLabel("db."), 0, 2)
        self.db_input = QLineEdit()
        self.db_input.setFixedWidth(60)
        input_grid.addWidget(self.db_input, 1, 2)

        input_grid.addWidget(QLabel("Élzárás"), 0, 3)
        self.elzaras_input = QLineEdit()
        self.elzaras_input.setFixedWidth(60)
        input_grid.addWidget(self.elzaras_input, 1, 3)

        self.duplung_checkbox = QCheckBox("Duplung")
        self.duplung_combobox = QComboBox()
        self.duplung_combobox.addItems(["Szín", "Fehér"])
        self.duplung_combobox.setEnabled(False)
        self.duplung_checkbox.stateChanged.connect(lambda state: self.duplung_combobox.setEnabled(state == Qt.Checked))
        input_grid.addWidget(self.duplung_checkbox, 2, 0)
        input_grid.addWidget(self.duplung_combobox, 2, 1)

        input_grid.addWidget(QLabel("Nút"), 3, 0)
        self.nut_input = QLineEdit()
        self.nut_input.setFixedWidth(60)
        input_grid.addWidget(self.nut_input, 3, 1)

        input_grid.addWidget(QLabel("Falc"), 3, 2)
        self.falc_input = QLineEdit()
        self.falc_input.setFixedWidth(60)
        input_grid.addWidget(self.falc_input, 3, 3)

        self.forgathato_checkbox = QCheckBox("Forgatható")
        input_grid.addWidget(self.forgathato_checkbox, 4, 0)

        self.uj_sor_gomb = QPushButton("Új sor hozzáadása")
        self.uj_sor_gomb.setDefault(True)
        self.uj_sor_gomb.setAutoDefault(True)
        input_grid.addWidget(self.uj_sor_gomb, 5, 0, 1, 4)

        bottom_row_layout.addWidget(meretek_group, alignment=Qt.AlignLeft)

        # Élzárás kiválasztása blokk
        elzaras_group = QGroupBox("- Élzárás kiválasztása")
        elzaras_layout = QVBoxLayout(elzaras_group)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Szálirány"))
        header_layout.addSpacing(30)
        header_layout.addWidget(QLabel("Keresztirány"))
        elzaras_layout.addLayout(header_layout)

        grid = QGridLayout()
        grid.setVerticalSpacing(3)
        grid.addWidget(QLabel("Típus"), 0, 0)
        self.elzaras_radios = []
        self.elzaras_groups = [QButtonGroup(self) for _ in range(4)]
        for group in self.elzaras_groups:
            group.setExclusive(True)

        for i in range(7):
            label = QLabel(str(i))
            grid.addWidget(label, i + 1, 0)
            row_radios = []
            for j in range(4):
                radio = QRadioButton()
                radio.setMaximumWidth(20)
                self.elzaras_groups[j].addButton(radio)
                grid.addWidget(radio, i + 1, j + 1)
                row_radios.append(radio)
            btn = QPushButton("mind")
            btn.setFixedWidth(40)
            btn.clicked.connect(lambda _, r=i: self.set_all_radios_in_row(r))
            grid.addWidget(btn, i + 1, 5)
            self.elzaras_radios.append(row_radios)

        elzaras_layout.addLayout(grid)
        bottom_row_layout.addWidget(elzaras_group, alignment=Qt.AlignLeft)
        
                # Munkaszám/Név/Elem/Megjegyzés blokk
        info_group = QGroupBox("- Egyéb adatok")
        info_layout = QGridLayout(info_group)
        info_layout.setAlignment(Qt.AlignTop)
        info_layout.setHorizontalSpacing(10)
        info_layout.setVerticalSpacing(5)

        self.munkaszam_input = QLineEdit()
        self.nev_input = QLineEdit()
        self.elem_input = QLineEdit()
        self.megjegyzes_input = QLineEdit()

        info_layout.addWidget(QLabel("Munkaszám"), 0, 0)
        info_layout.addWidget(self.munkaszam_input, 1, 0)

        info_layout.addWidget(QLabel("Név"), 0, 1)
        info_layout.addWidget(self.nev_input, 1, 1)

        info_layout.addWidget(QLabel("Elem"), 2, 0)
        info_layout.addWidget(self.elem_input, 3, 0)

        info_layout.addWidget(QLabel("Megjegyzés"), 2, 1)
        info_layout.addWidget(self.megjegyzes_input, 3, 1)
        
        bottom_row_layout.addWidget(info_group, stretch=1)


        lower_layout.addWidget(bottom_row_wrapper)
        lower_widget.setLayout(lower_layout)
        splitter.addWidget(lower_widget)
        splitter.setStretchFactor(1, 2)

        self.setLayout(main_layout)

        self.szali_input.returnPressed.connect(lambda: self._fokusz_valtas(self.kereszt_input, clear=True))
        self.kereszt_input.returnPressed.connect(lambda: self._fokusz_valtas(self.db_input, clear=True))
        self.db_input.returnPressed.connect(lambda: self._fokusz_valtas(self.elzaras_input, clear=False))
        self.elzaras_input.returnPressed.connect(self.uj_sor_hozzaadas)
        self.uj_sor_gomb.clicked.connect(self.uj_sor_hozzaadas)

        for col in range(4):
            for row in range(7):
                self.elzaras_radios[row][col].toggled.connect(self.update_elzaras_input)

        self.elzaras_input.textChanged.connect(self.sync_radios_with_elzaras_input)

        self.update_elzaras_input()
        
        self.anyag_input.textChanged.connect(self.filter_anyagok)  
        main_layout.addWidget(self.anyag_suggestions)  # a végén vagy közvetlenül az input után

        
    def _fokusz_valtas(self, widget, clear=False):
        if clear:
            widget.clear()
        else:
            widget.selectAll()
        widget.setFocus()

    def uj_sor_hozzaadas(self):
        # Ne lehessen üres méretekkel vagy darabszámmal sort hozzáadni
        if not self.szali_input.text().strip() or not self.kereszt_input.text().strip() or not self.db_input.text().strip():
            return  # semmit ne csináljon, ha bármelyik mező üres

        row = self.lista_table.rowCount()
        self.lista_table.insertRow(row)

        checkbox = QCheckBox()
        self.lista_table.setCellWidget(row, 0, checkbox)

        values = [
            str(row + 1),
            self.szali_input.text(),
            self.kereszt_input.text(),
            self.db_input.text(),
            self.elzaras_input.text(),
            "✔" if self.forgathato_checkbox.isChecked() else "",
            self.munkaszam_input.text(),
            self.nev_input.text(),
            self.elem_input.text(),
            self.megjegyzes_input.text()
        ]

        for col, val in enumerate(values, start=1):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignCenter)
            self.lista_table.setItem(row, col, item)

        self.szali_input.clear()
        self.kereszt_input.clear()
        self.db_input.clear()
        self._fokusz_valtas(self.szali_input, clear=True)
        self.anyag_input.textEdited.connect(self._javaslat_pozicionalas)

    
        
    def toggle_all_anyagok_checkboxes(self):
        for row in range(self.anyagok_table.rowCount()):
            cb = self.anyagok_table.cellWidget(row, 0)
            if isinstance(cb, QCheckBox):
                cb.setChecked(self.select_all_checkbox.isChecked())

    def set_all_radios_in_row(self, row):
        for col in range(4):
            self.elzaras_radios[row][col].setChecked(True)

    def update_elzaras_input(self):
        value = ""
        for col in range(4):
            for row in range(7):
                if self.elzaras_radios[row][col].isChecked():
                    value += str(row)
                    break
            else:
                value += "0"
        self.elzaras_input.setText(value)

    def sync_radios_with_elzaras_input(self):
        text = self.elzaras_input.text()
        if not text.isdigit() or len(text) != 4:
            return
        for col, char in enumerate(text[:4]):
            idx = int(char)
            if 0 <= idx < 7:
                self.elzaras_radios[idx][col].setChecked(True)
    
    def filter_anyagok(self, text):
        self.anyag_suggestions.clear()

        if not text:
            self.anyag_suggestions.hide()
            return

        filtered = [a for a in self.anyag_lista if text.lower() in str(a).lower()]
        if not filtered:
            self.anyag_suggestions.hide()
            return

        for item in filtered:
            self.anyag_suggestions.addItem(QListWidgetItem(str(item)))

    def select_suggestion(self, item):
        self.anyag_input.setText(item.text())
        self.anyag_suggestions.hide()
        self.anyag_input.setFocus()
        
    def eventFilter(self, obj, event):
        if obj == self.anyag_input:
            if event.type() == QEvent.KeyPress:
                key = event.key()
                if key == Qt.Key_Down and self.anyag_suggestions.isVisible():
                    self.anyag_suggestions.setFocus()
                    self.anyag_suggestions.setCurrentRow(0)
                    return True
        elif obj == self.anyag_suggestions:
            if event.type() == QEvent.KeyPress:
                key = event.key()
                if key == Qt.Key_Escape:
                    self.anyag_suggestions.hide()
                    self.anyag_input.setFocus()
                    return True
                elif key == Qt.Key_Return or key == Qt.Key_Enter:
                    current_item = self.anyag_suggestions.currentItem()
                    if current_item:
                        self.select_suggestion(current_item)
                    return True
        return super().eventFilter(obj, event)
        
        def show_suggestions():
            pos = self.anyag_input.mapToGlobal(QPoint(0, self.anyag_input.height()))
            self.anyag_suggestions.move(pos)
            self.anyag_suggestions.resize(self.anyag_input.width(), self.anyag_suggestions.sizeHintForRow(0) * min(6, len(filtered)) + 4)
            self.anyag_suggestions.show()

        QTimer.singleShot(0, show_suggestions)  


        def eventFilter(self, obj, event):
            if obj == self.anyag_dropdown and event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Escape:
                    self.anyag_dropdown.hide()
                    self.anyag_input.setFocus()
                    return True
            return super().eventFilter(obj, event)
        
        def eventFilter(self, obj, event):
            if obj == self.anyag_dropdown and event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Escape:
                    self.anyag_dropdown.hide()
                    self.anyag_input.setFocus()
                    return True
                elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
                    self.set_anyag_input(self.anyag_dropdown.currentText())
                    return True
                elif event.key() in (Qt.Key_Up, Qt.Key_Down):
                    return False  # engedjük a QComboBox-nak kezelni
            return super().eventFilter(obj, event)

    def set_anyag_input(self, value):
        self.anyag_input.setText(value)
        self.anyag_dropdown.hide()
        self.anyag_input.setFocus()

    def _anyag_kivalasztva(self, item):
        self.anyag_input.setText(item.text())
        self.anyag_suggestions.hide()
        self.anyag_input.setFocus()

    def _anyag_szures(self, text):
        self.anyag_suggestions.clear()
        if not text.strip():
            self.anyag_suggestions.hide()
            return
        filtered = [a for a in self.anyag_lista if text.lower() in str(a).lower()]
        if filtered:
            for item in filtered[:20]:
                self.anyag_suggestions.addItem(str(item))
            self._javaslat_pozicionalas()
            self.anyag_suggestions.setCurrentRow(0)
            self.anyag_suggestions.show()
        else:
            self.anyag_suggestions.hide()
            
    def _javaslat_pozicionalas(self):
        pos = self.anyag_input.mapToGlobal(self.anyag_input.rect().bottomLeft())
        self.anyag_suggestions.move(pos)
        
    def eventFilter(self, obj, event):
        if obj == self.anyag_input and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Down, Qt.Key_Up):
                self.anyag_suggestions.setFocus()
                self.anyag_suggestions.setCurrentRow(0)
                return True
            elif event.key() == Qt.Key_Escape:
                self.anyag_suggestions.hide()
                return True
            elif event.key() == Qt.Key_Return:
                if self.anyag_suggestions.isVisible() and self.anyag_suggestions.currentItem():
                    self._anyag_kivalasztva(self.anyag_suggestions.currentItem())
                    return True
        elif obj == self.anyag_suggestions and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return:
                self._anyag_kivalasztva(self.anyag_suggestions.currentItem())
                return True
            elif event.key() == Qt.Key_Escape:
                self.anyag_suggestions.hide()
                self.anyag_input.setFocus()
                return True
        return super().eventFilter(obj, event)