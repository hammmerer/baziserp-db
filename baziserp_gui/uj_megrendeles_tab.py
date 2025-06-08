
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidget
import pandas as pd

class UjMegrendelesTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Anyaglista betöltése
        try:
            self.anyagok_df = pd.read_excel("anyaglista.xlsx")
            self.anyagok = self.anyagok_df["megnevezés"].dropna().tolist()
        except Exception as e:
            self.anyagok = ["Hiba az anyaglista betöltésekor"]

        self.label = QLabel("Anyag keresése:")
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.update_list)

        self.list_widget = QListWidget()
        self.update_list()

        layout.addWidget(self.label)
        layout.addWidget(self.search_box)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def update_list(self):
        query = self.search_box.text().casefold()
        self.list_widget.clear()
        for item in self.anyagok:
            if query in item.casefold():
                self.list_widget.addItem(item)
