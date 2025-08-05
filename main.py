import sys
from PyQt5.QtWidgets import QApplication, QMessageBox

from db.db import initialize_database_if_needed
from ui.main_window import  ModernApp
# from db.database import init_db

def main():
    try:
        # Initialize database (creates folder + table if needed)
        initialize_database_if_needed()

        app = QApplication(sys.argv)
        # window = TailwindStyleApp()
        window = ModernApp()
        window.show()
        sys.exit(app.exec_())

    except Exception as e:
        # Show any startup errors in a user-friendly message box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Application Error")
        msg.setText("An unexpected error occurred during startup.")
        msg.setDetailedText(str(e))
        msg.exec_()
        sys.exit(1)

if __name__ == '__main__':
    main()
