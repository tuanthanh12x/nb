from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QFormLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QHBoxLayout, QFrame, QGridLayout, QInputDialog
)
from PyQt5.QtCore import Qt, QSize
from functools import partial
import qtawesome as qta

# Sửa lại import để bao gồm hàm mới và các hàm đã được cập nhật
from core.user_manager import get_all_users, add_user, delete_user, update_user_password


class UserManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self._setup_connections()
        self._refresh_user_table()

    def init_ui(self):
        """Khởi tạo giao diện người dùng."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignTop)

        # --- Tiêu đề chính và nút Tải lại ---
        title_layout = QHBoxLayout()
        title = QLabel("👤 Quản lý Người dùng")
        title.setObjectName("h2")
        title_layout.addWidget(title)
        title_layout.addStretch()
        self.refresh_btn = QPushButton(qta.icon("fa5s.sync-alt"), " Tải lại")
        title_layout.addWidget(self.refresh_btn)
        main_layout.addLayout(title_layout)

        # --- Bố cục chính với 2 cột ---
        content_layout = QGridLayout()
        content_layout.setSpacing(20)
        main_layout.addLayout(content_layout)

        # --- Cột 1: Form thêm người dùng ---
        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_card_layout = QVBoxLayout(form_card)
        form_card_layout.setSpacing(15)

        form_title = QLabel("Thêm người dùng mới")
        form_title.setObjectName("h3")

        form = QFormLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập...")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu...")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Admin", "Guest"])  # Guest là vai trò có quyền thấp nhất

        form.addRow("Tên đăng nhập:", self.username_input)
        form.addRow("Mật khẩu:", self.password_input)
        form.addRow("Vai trò:", self.role_combo)

        self.add_btn = QPushButton(qta.icon("fa5s.user-plus", color="white"), "  Thêm mới")
        self.add_btn.setObjectName("submitButton")

        form_card_layout.addWidget(form_title)
        form_card_layout.addLayout(form)
        form_card_layout.addWidget(self.add_btn, 0, Qt.AlignRight)
        form_card_layout.addStretch()

        content_layout.addWidget(form_card, 0, 0)

        # --- Cột 2: Bảng danh sách người dùng ---
        table_card = QFrame()
        table_card.setObjectName("formCard")
        table_card_layout = QVBoxLayout(table_card)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["ID", "Tên đăng nhập", "Vai trò", "Hành động"])
        self.user_table.setColumnHidden(0, True)  # Ẩn cột ID
        self.user_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.user_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.user_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)

        table_card_layout.addWidget(self.user_table)
        content_layout.addWidget(table_card, 0, 1)

        content_layout.setColumnStretch(0, 1)  # Form co giãn 1 phần
        content_layout.setColumnStretch(1, 2)  # Bảng co giãn 2 phần

    def _setup_connections(self):
        """Kết nối các tín hiệu (signals) tới các khe (slots)."""
        self.add_btn.clicked.connect(self._handle_add_user)
        self.refresh_btn.clicked.connect(self._refresh_user_table)

    def _refresh_user_table(self):
        """Làm mới dữ liệu trong bảng người dùng."""
        self.user_table.setRowCount(0)
        try:
            users = get_all_users()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi cơ sở dữ liệu", f"Không thể tải danh sách người dùng:\n{e}")
            return

        for user in users:
            row_position = self.user_table.rowCount()
            self.user_table.insertRow(row_position)

            self.user_table.setItem(row_position, 0, QTableWidgetItem(str(user["id"])))
            self.user_table.setItem(row_position, 1, QTableWidgetItem(user["username"]))
            self.user_table.setItem(row_position, 2, QTableWidgetItem(user["role"]))

            # Tạo widget chứa các nút hành động
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            actions_layout.setSpacing(5)

            # Nút đổi mật khẩu
            change_pw_btn = QPushButton(qta.icon("fa5s.key"), "")
            change_pw_btn.setToolTip("Đổi mật khẩu")
            change_pw_btn.setCursor(Qt.PointingHandCursor)
            # Nút xóa
            delete_btn = QPushButton(qta.icon("fa5s.trash-alt"), "")
            delete_btn.setToolTip("Xóa người dùng")
            delete_btn.setObjectName("deleteButton")  # Để có style riêng nếu muốn
            delete_btn.setCursor(Qt.PointingHandCursor)

            # Kết nối sự kiện với ID và username cụ thể của hàng đó
            change_pw_btn.clicked.connect(partial(self._handle_change_password, user["id"], user["username"]))
            delete_btn.clicked.connect(partial(self._handle_delete_user, user["id"], user["username"]))

            actions_layout.addWidget(change_pw_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()

            self.user_table.setCellWidget(row_position, 3, actions_widget)

    def _handle_add_user(self):
        """Xử lý logic khi nhấn nút thêm người dùng."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_combo.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        success, msg = add_user(username, password, role)
        if success:
            QMessageBox.information(self, "Thành công", msg)
            self.username_input.clear()
            self.password_input.clear()
            self._refresh_user_table()
        else:
            QMessageBox.critical(self, "Thất bại", msg)

    def _handle_delete_user(self, user_id, username):
        """Xử lý logic khi nhấn nút xóa người dùng."""
        confirm = QMessageBox.question(self, "Xác nhận xóa",
                                       f"Bạn có chắc chắn muốn xóa người dùng '{username}' không?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            success, msg = delete_user(user_id)
            if success:
                QMessageBox.information(self, "Thành công", f"Đã xóa người dùng '{username}'.")
                self._refresh_user_table()
            else:
                QMessageBox.critical(self, "Lỗi", msg)

    def _handle_change_password(self, user_id, username):
        """Xử lý logic khi nhấn nút đổi mật khẩu."""
        new_password, ok = QInputDialog.getText(self, "Đổi mật khẩu", f"Nhập mật khẩu mới cho '{username}':",
                                                QLineEdit.Password)

        if ok and new_password:
            success, msg = update_user_password(user_id, new_password)
            if success:
                QMessageBox.information(self, "Thành công", msg)
            else:
                QMessageBox.critical(self, "Lỗi", msg)
        elif ok and not new_password:
            QMessageBox.warning(self, "Hủy bỏ", "Mật khẩu không được để trống.")


# Hàm để gọi từ bên ngoài (nếu cần)
def create_user_management_page():
    return UserManagementPage()