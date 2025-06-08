import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtCore import Qt
from szabaszat_tab import SzabaszatTab
from uj_szabaszat import UjMegrendelesTab
from anyag_tab import AnyagokTab



class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lapszabászat rendszer - BazisERP")
        self.setWindowState(Qt.WindowMaximized)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)

        self.add_custom_tab("A szabászat menete", SzabaszatTab())
        self.add_empty_tab("Naptár")
        self.add_custom_tab("Új megrendelés felvétele", UjMegrendelesTab())
        self.add_custom_tab("Anyagok kezelése", AnyagokTab())
        self.add_empty_tab("Optimalizálás")
        self.add_empty_tab("Beállítások")

        self.setCentralWidget(self.tabs)
        self.tabs.setCurrentIndex(3)
        
    def add_custom_tab(self, title, widget):
        self.tabs.addTab(widget, title)

    def add_empty_tab(self, title):
        from PyQt5.QtWidgets import QWidget
        self.tabs.addTab(QWidget(), title)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
