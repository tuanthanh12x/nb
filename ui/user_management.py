# ui/user_management.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
import qtawesome as qta
import bcrypt

from db.database import get_db_session, User


class UserDialog(QDialog):
    """Cửa sổ dialog để thêm hoặc sửa thông tin người dùng."""
    # Tín hiệu sẽ được phát ra khi lưu thành công
    user_saved = pyqtSignal()

    def __init__(self, user_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.is_edit_mode = user_id is not None
        self.setWindowTitle("Sửa Người dùng" if self.is_edit_mode else "Thêm Người dùng mới")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.full_name_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])

        form_layout.addRow("Tên đăng nhập:", self.username_input)
        form_layout.addRow("Họ và Tên:", self.full_name_input)
        pwd_label = "Mật khẩu (bỏ trống nếu không đổi):" if self.is_edit_mode else "Mật khẩu:"
        form_layout.addRow(pwd_label, self.password_input)
        form_layout.addRow("Vai trò:", self.role_combo)

        layout.addLayout(form_layout)

        # Nút Save và Cancel
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        if self.is_edit_mode:
            self.load_user_data()

    def load_user_data(self):
        """Tải dữ liệu của người dùng vào form để chỉnh sửa."""
        session = next(get_db_session())
        user = session.query(User).filter_by(id=self.user_id).first()
        session.close()

        if user:
            self.username_input.setText(user.username)
            self.username_input.setReadOnly(True)  # Không cho sửa username
            self.full_name_input.setText(user.full_name)
            self.role_combo.setCurrentText(user.role)

    def accept(self):
        """Xử lý khi nhấn nút Save."""
        session = next(get_db_session())
        try:
            username = self.username_input.text().strip()
            full_name = self.full_name_input.text().strip()
            password = self.password_input.text()
            role = self.role_combo.currentText()

            if not username or not full_name:
                QMessageBox.warning(self, "Lỗi", "Tên đăng nhập và Họ tên không được để trống.")
                return

            if self.is_edit_mode:
                # Chế độ Sửa
                user = session.query(User).filter_by(id=self.user_id).first()
                user.full_name = full_name
                user.role = role
                if password:  # Chỉ cập nhật mật khẩu nếu người dùng nhập
                    user.set_password(password)
            else:
                # Chế độ Thêm mới
                if not password:
                    QMessageBox.warning(self, "Lỗi", "Mật khẩu không được để trống khi tạo mới.")
                    return
                # Kiểm tra username đã tồn tại chưa
                existing_user = session.query(User).filter_by(username=username).first()
                if existing_user:
                    QMessageBox.warning(self, "Lỗi", "Tên đăng nhập đã tồn tại.")
                    return

                new_user = User(username=username, full_name=full_name, role=role)
                new_user.set_password(password)
                session.add(new_user)

            session.commit()
            self.user_saved.emit()  # Phát tín hiệu
            super().accept()  # Đóng dialog
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Lỗi CSDL", f"Đã có lỗi xảy ra: {e}")
        finally:
            session.close()


class UserManagementPage(QWidget):
    """Trang quản lý người dùng."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # Tham chiếu tới cửa sổ chính

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)

        # --- Tiêu đề và Nút hành động ---
        header_layout = QHBoxLayout()
        title = QLabel("Quản lý Người dùng 👥")
        title.setObjectName("h2")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.add_btn = QPushButton(" Thêm người dùng")
        self.add_btn.setIcon(qta.icon("fa5s.user-plus", color="white"))
        self.add_btn.setObjectName("submitButton")
        self.add_btn.clicked.connect(self.add_user)
        header_layout.addWidget(self.add_btn)

        layout.addLayout(header_layout)

        # --- Bảng hiển thị người dùng ---
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(["ID", "Tên đăng nhập", "Họ và Tên", "Vai trò", "Hành động"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.verticalHeader().setVisible(False)
        layout.addWidget(self.user_table)

        self.load_users()

    def load_users(self):
        """Tải danh sách người dùng từ CSDL vào bảng."""
        self.user_table.setRowCount(0)
        session = next(get_db_session())
        users = session.query(User).all()
        session.close()

        for row, user in enumerate(users):
            self.user_table.insertRow(row)
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.username))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.full_name))
            self.user_table.setItem(row, 3, QTableWidgetItem(user.role))

            # Tạo các nút hành động
            action_widget = self._create_action_buttons(user.id)
            self.user_table.setCellWidget(row, 4, action_widget)

        self.user_table.resizeRowsToContents()

    def _create_action_buttons(self, user_id):
        """Tạo các nút Sửa và Xóa cho mỗi dòng."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        edit_btn = QPushButton()
        edit_btn.setIcon(qta.icon("fa5s.edit", color="#F59E0B"))
        edit_btn.setToolTip("Sửa người dùng")
        edit_btn.clicked.connect(lambda: self.edit_user(user_id))

        delete_btn = QPushButton()
        delete_btn.setIcon(qta.icon("fa5s.trash-alt", color="#EF4444"))
        delete_btn.setToolTip("Xóa người dùng")
        delete_btn.clicked.connect(lambda: self.delete_user(user_id))

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def add_user(self):
        """Mở dialog để thêm người dùng mới."""
        dialog = UserDialog(parent=self)
        dialog.user_saved.connect(self.load_users)  # Kết nối tín hiệu để reload bảng
        dialog.exec_()

    def edit_user(self, user_id):
        """Mở dialog để sửa thông tin người dùng."""
        dialog = UserDialog(user_id=user_id, parent=self)
        dialog.user_saved.connect(self.load_users)
        dialog.exec_()

    def delete_user(self, user_id):
        """Xóa người dùng khỏi CSDL sau khi xác nhận."""
        session = next(get_db_session())
        user_to_delete = session.query(User).filter_by(id=user_id).first()

        if not user_to_delete:
            session.close()
            return

        # Không cho xóa chính mình
        if user_to_delete.username.lower() == self.main_window.current_user.lower():
            QMessageBox.warning(self, "Không thể xóa", "Bạn không thể xóa tài khoản đang đăng nhập.")
            session.close()
            return

        reply = QMessageBox.question(self, 'Xác nhận xóa',
                                     f"Bạn có chắc chắn muốn xóa người dùng '{user_to_delete.username}' không?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                session.delete(user_to_delete)
                session.commit()
                self.load_users()  # Tải lại bảng
                QMessageBox.information(self, "Thành công", f"Đã xóa người dùng '{user_to_delete.username}'.")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Lỗi CSDL", f"Không thể xóa người dùng: {e}")
            finally:
                session.close()
        else:
            session.close()


def create_user_management_page(parent):
    """Hàm khởi tạo để dễ dàng gọi từ cửa sổ chính."""
    return UserManagementPage(parent)