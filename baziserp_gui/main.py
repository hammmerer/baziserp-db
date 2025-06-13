import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QDialog
from PyQt5.QtCore import Qt
from szabaszat_tab import SzabaszatTab
from uj_szabaszat import UjMegrendelesTab
from anyag_tab import AnyagokTab
from egyedi_munkak import EgyediMunkakTab
from login_dialog import LoginDialog  # ⬅️ ÚJ: importáljuk a login dialógust

class MainApp(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle(f"Lapszabászat rendszer - BazisERP ({user_data['username']})")
        self.setWindowState(Qt.WindowMaximized)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)

        self.add_custom_tab("A szabászat menete", SzabaszatTab())
        self.add_custom_tab("Egyedi munkák", EgyediMunkakTab())
        self.add_empty_tab("Naptár")
        self.add_custom_tab("Új megrendelés felvétele", UjMegrendelesTab())
        self.add_custom_tab("Anyagok kezelése", AnyagokTab())
        self.add_empty_tab("Optimalizálás")
        self.add_empty_tab("Beállítások")


        
        self.setCentralWidget(self.tabs)
        self.tabs.setCurrentIndex(1)
        
    def add_custom_tab(self, title, widget):
        self.tabs.addTab(widget, title)

    def add_empty_tab(self, title):
        from PyQt5.QtWidgets import QWidget
        self.tabs.addTab(QWidget(), title)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ⬇️ Bejelentkezési ablak megnyitása
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        user_data = login.user_data
        window = MainApp(user_data)  # átadjuk a bejelentkezett felhasználót
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit()  # kilépés, ha nem jelentkezett be
