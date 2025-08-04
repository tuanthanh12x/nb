# run.py

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from ui.login import LoginWindow
from main import ModernApp
from db.database import create_tables

main_window = None

def show_main_app(username):
    global main_window
    main_window = ModernApp(username=username)
    main_window.show()

def main():
    create_tables()
    app = QApplication(sys.argv)
    font = QFont("Segoe UI")
    app.setFont(font)
    login = LoginWindow()
    login.login_successful.connect(show_main_app)
    login.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()