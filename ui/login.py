# login_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
import bcrypt

# Giả định các file này nằm trong cùng thư mục hoặc trong Python path
from db.database import get_db_session, User
from ui.styles import get_global_stylesheet

class LoginWindow(QWidget):
    """
    Cửa sổ đăng nhập.
    Phát ra tín hiệu 'login_successful' khi đăng nhập thành công.
    """
    login_successful = pyqtSignal(str)  # Tín hiệu mang theo username

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng nhập")
        self.setFixedSize(350, 200)
        self.setStyleSheet(get_global_stylesheet())  # Sử dụng style chung

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Hệ thống Cấp số Văn bản")
        title.setObjectName("h2")
        title.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tài khoản (admin)")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu (admin)")
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Tài khoản:", self.username_input)
        form_layout.addRow("Mật khẩu:", self.password_input)

        login_button = QPushButton("Đăng nhập")
        login_button.setObjectName("submitButton")
        login_button.clicked.connect(self._handle_login)
        # Cho phép nhấn Enter để đăng nhập
        self.password_input.returnPressed.connect(self._handle_login)

        layout.addWidget(title)
        layout.addSpacing(15)
        layout.addLayout(form_layout)
        layout.addSpacing(15)
        layout.addWidget(login_button)

    def _handle_login(self):
        """Xử lý logic đăng nhập bằng cách truy vấn CSDL."""
        username = self.username_input.text()
        password = self.password_input.text().encode('utf-8')  # Mã hóa password sang bytes

        db_session = get_db_session()
        try:
            # Tìm người dùng trong CSDL
            user = db_session.query(User).filter(User.username == username).first()

            if user:
                # Kiểm tra mật khẩu đã băm
                password_hash_from_db = user.password_hash.encode('utf-8')
                if bcrypt.checkpw(password, password_hash_from_db):
                    self.login_successful.emit(user.username)  # Gửi username đi
                    self.close()
                else:
                    QMessageBox.warning(self, "Lỗi đăng nhập", "Mật khẩu không chính xác!")
            else:
                QMessageBox.warning(self, "Lỗi đăng nhập", f"Tài khoản '{username}' không tồn tại.")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi CSDL", f"Có lỗi xảy ra khi truy vấn:\n{e}")
        finally:
            db_session.close()  # Đóng session sau khi hoàn thành