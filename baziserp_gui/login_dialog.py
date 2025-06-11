import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)

CONFIG_PATH = "config.json"

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bejelentkezés")
        self.setFixedSize(300, 150)

        # Felhasználónév mező
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Felhasználónév")
        self.username_input.setText(self.load_last_username())

        # PIN (jelszó) mező
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("PIN")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Bejelentkezés gomb
        self.login_button = QPushButton("Bejelentkezés")
        self.login_button.clicked.connect(self.authenticate)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Felhasználónév:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("PIN kód:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        self.user_data = None

    def load_last_username(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    config = json.load(f)
                    return config.get("last_username", "")
            except:
                return ""
        return ""

    def save_last_username(self, username):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"last_username": username}, f)

    def authenticate(self):
        # IDEIGLENES LOGIN ÁTUGRÁS (fejlesztési célra)
        self.user_data = {
            "id": 1,
            "username": "admin",
            "roles": ["Admin"]
        }
        self.accept()

#    def authenticate(self):
 #       username = self.username_input.text().strip()
  #      pin = self.password_input.text()
#
 #       try:
  #          # Kapcsolódás Supabase PostgreSQL-hez
   #         conn = psycopg2.connect(
    ##        host="db.zrowugsybqzlnvypspqj.supabase.co",
      #      dbname="postgres",
       #     user="postgres",
        #    password="4Bignaggi7",                    # jelszó innen
#            port=5432
 #       )
#
 #           cur = conn.cursor(cursor_factory=RealDictCursor)
#
 #           # Felhasználó lekérése
  #          cur.execute("""
   ##             SELECT id, nev, pin
     #           FROM users
      #          WHERE nev = %s AND aktiv = true
       #     """, (username,))
        ##    user = cur.fetchone()
##
  ###          if not user:
     #           QMessageBox.warning(self, "Hiba", "Nincs ilyen aktív felhasználó")
      ##          return
##
  #          if not check_password_hash(user["pin"], pin):
   #             QMessageBox.warning(self, "Hiba", "Hibás PIN kód")
    ##            return
#
 ####           # Szerepkörök lekérdezése
     #       cur.execute("""
      #          SELECT r.nev
       ###         FROM roles r
          #      JOIN user_roles ur ON ur.role_id = r.id
#                WHERE ur.user_id = %s
 #           """, (user["id"],))
  #          roles = [r["nev"] for r in cur.fetchall()]
#
 #           self.save_last_username(username)
  #          self.user_data = {
   #####             "id": user["id"],
        #        "username": user["nev"],
#                "roles": roles
 #           }
 #           self.accept()
#
 ##       except Exception as e:
   #         QMessageBox.critical(self, "Hiba", f"Adatbázishiba:\n{str(e)}")
#
 ##       finally:
   #         if 'conn' in locals():
    #            conn.close()
