import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui.main_window import ModernApp, LoginWindow

from db.database import get_db_session, User, create_tables
from sqlalchemy.orm import Session
import bcrypt # Thư viện để băm mật khẩu
def main():
    try:

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI")
    app.setFont(font)

    # Biến để giữ tham chiếu đến cửa sổ chính, tránh bị xóa
    main_window = None

    def show_main_app(username):
        """Hàm để tạo và hiển thị cửa sổ chính sau khi đăng nhập."""
        global main_window
        main_window = ModernApp(username=username)
        main_window.show()

    # Tạo và hiển thị cửa sổ đăng nhập
    login_window = LoginWindow()
    # Kết nối tín hiệu đăng nhập thành công với hàm hiển thị cửa sổ chính
    login_window.login_successful.connect(show_main_app)
    login_window.show()

    sys.exit(app.exec_())