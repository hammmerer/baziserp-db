from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QTableWidget, QTableWidgetItem,
    QGroupBox, QCheckBox, QGridLayout, QHeaderView
)
from PyQt5.QtCore import Qt
import pandas as pd


class AnyagokTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_anyaglista()

    def load_anyaglista(self):
        try:
            df = pd.read_excel("baziserp_gui/anyaglista.xlsx")  # vagy használd a teljes elérési utat
            megnevezesek = df["megnevezés"].dropna().tolist()
            self.anyag_list.clear()
            for nev in megnevezesek:
                self.anyag_list.addItem(nev)
        except Exception as e:
            print(f"Hiba az anyaglista betöltésekor: {e}")

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # BAL PANEL – Anyaglista
        bal_panel = QVBoxLayout()
        bal_panel.addWidget(QLabel("📦 Anyaglista"))

        self.anyag_list = QListWidget()
        bal_panel.addWidget(self.anyag_list)

        btn_layout = QHBoxLayout()
        self.btn_up = QPushButton("⬆")
        self.btn_down = QPushButton("⬇")
        btn_layout.addWidget(self.btn_up)
        btn_layout.addWidget(self.btn_down)
        bal_panel.addLayout(btn_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Keresés...")
        bal_panel.addWidget(self.search_input)

        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("Tábla méret")
        bal_panel.addWidget(self.size_input)

        bal_group = QGroupBox("Beállítások")
        bal_form = QGridLayout()
        self.szelesseg_input = QLineEdit()
        self.hossz_input = QLineEdit()
        self.forgathato_cb = QCheckBox("Forgatható")
        self.riasztas_cb = QCheckBox("Riasztás")
        bal_form.addWidget(QLabel("Szélesség:"), 0, 0)
        bal_form.addWidget(self.szelesseg_input, 0, 1)
        bal_form.addWidget(QLabel("Hossz:"), 1, 0)
        bal_form.addWidget(self.hossz_input, 1, 1)
        bal_form.addWidget(self.forgathato_cb, 2, 0, 1, 2)
        bal_form.addWidget(self.riasztas_cb, 3, 0, 1, 2)
        bal_group.setLayout(bal_form)
        bal_panel.addWidget(bal_group)

        main_layout.addLayout(bal_panel, 2)

        # KÖZÉPSŐ PANEL – Készlet tábla
        kozep_panel = QVBoxLayout()
        kozep_panel.addWidget(QLabel("📋 Készlet lista"))

        self.keszlet_table = QTableWidget(0, 4)
        self.keszlet_table.setHorizontalHeaderLabels(["Szél.", "Ker.", "Megjegyzés", "db"])
        self.keszlet_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        kozep_panel.addWidget(self.keszlet_table)

        self.forgathato_kozep_cb = QCheckBox("Forgatható")
        self.maradek_cb = QCheckBox("Csak maradék")
        kozep_panel.addWidget(self.forgathato_kozep_cb)
        kozep_panel.addWidget(self.maradek_cb)

        self.leltar_btn = QPushButton("📄 Tábla anyag leltár")
        kozep_panel.addWidget(self.leltar_btn)

        main_layout.addLayout(kozep_panel, 3)

        # JOBB PANEL – Élzárók
        jobb_panel = QVBoxLayout()
        jobb_panel.addWidget(QLabel("Élzárók"))

        self.elzaro_list = QListWidget()
        jobb_panel.addWidget(self.elzaro_list)

        self.elzaro_input = QLineEdit()
        self.elzaro_input.setPlaceholderText("Élzáró neve")
        self.elzaro_ar_input = QLineEdit()
        self.elzaro_ar_input.setPlaceholderText("Egységár (HUF/m)")
        self.elzaro_vastagsag_input = QLineEdit()
        self.elzaro_vastagsag_input.setPlaceholderText("Vastagság (mm)")

        jobb_panel.addWidget(self.elzaro_input)
        jobb_panel.addWidget(self.elzaro_ar_input)
        jobb_panel.addWidget(self.elzaro_vastagsag_input)

        main_layout.addLayout(jobb_panel, 2)
