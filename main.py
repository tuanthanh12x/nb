# import sys
# from PyQt5.QtGui import QFont
# from PyQt5.QtWidgets import QApplication, QMessageBox
# from ui.main_window import ModernApp, LoginWindow
# from db.database import get_db_session, User, create_tables
# from sqlalchemy.orm import Session
# import bcrypt  # Thư viện để băm mật khẩu
#
# def show_main_app(username):
#     """Hàm để tạo và hiển thị cửa sổ chính sau khi đăng nhập."""
#     main_window = ModernApp(username=username)
#     main_window.show()
#     return main_window  # Trả về để giữ tham chiếu
#
# def main():
#     try:
#         app = QApplication(sys.argv)
#         font = QFont("Segoe UI")
#         app.setFont(font)
#
#         # Tạo và hiển thị cửa sổ đăng nhập
#         login_window = LoginWindow()
#
#         # Khi đăng nhập thành công → mở main app
#         main_window = None
#         def handle_login(username):
#             nonlocal main_window
#             main_window = show_main_app(username)
#
#         login_window.login_successful.connect(handle_login)
#         login_window.show()
#
#         sys.exit(app.exec_())
#
#     except Exception as e:
#         msg = QMessageBox()
#         msg.setIcon(QMessageBox.Critical)
#         msg.setWindowTitle("Application Error")
#         msg.setText("An unexpected error occurred during startup.")
#         msg.setDetailedText(str(e))
#         msg.exec_()
#         sys.exit(1)
#
# if __name__ == "__main__":
#     main()
