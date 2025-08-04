from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QFormLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QHBoxLayout
)
from PyQt5.QtCore import Qt
from core.user_manager import get_all_users, add_user, delete_user  # Sửa lại import

def create_user_management_page():
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(30, 20, 30, 30)
    layout.setSpacing(20)

    title = QLabel("👤 Quản lý Người dùng")
    title.setObjectName("h2")
    layout.addWidget(title)

    # --- Form thêm người dùng ---
    form = QFormLayout()
    username_input = QLineEdit()
    password_input = QLineEdit()
    password_input.setEchoMode(QLineEdit.Password)
    role_combo = QComboBox()
    role_combo.addItems(["Admin", "Guest"])
    add_btn = QPushButton("➕ Thêm người dùng")

    form.addRow("Tên đăng nhập:", username_input)
    form.addRow("Mật khẩu:", password_input)
    form.addRow("Vai trò:", role_combo)
    layout.addLayout(form)
    layout.addWidget(add_btn)

    # --- Bảng danh sách người dùng ---
    user_table = QTableWidget()
    user_table.setColumnCount(3)
    user_table.setHorizontalHeaderLabels(["Tên đăng nhập", "Vai trò", "Hành động"])
    user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    layout.addWidget(user_table)

    def refresh_table():
        user_table.setRowCount(0)
        try:
            users = get_all_users()
        except Exception as e:
            QMessageBox.critical(widget, "Lỗi cơ sở dữ liệu", str(e))
            return

        for i, user in enumerate(users):
            user_table.insertRow(i)
            user_table.setItem(i, 0, QTableWidgetItem(user["username"]))
            user_table.setItem(i, 1, QTableWidgetItem(user["role"]))

            delete_btn = QPushButton("❌ Xoá")
            delete_btn.clicked.connect(lambda _, u=user["username"]: handle_delete(u))
            user_table.setCellWidget(i, 2, delete_btn)

    def handle_add():
        username = username_input.text().strip()
        password = password_input.text().strip()
        role = role_combo.currentText()
        if not username or not password:
            QMessageBox.warning(widget, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return
        success, msg = add_user(username, password, role)
        if success:
            QMessageBox.information(widget, "Thành công", msg)
            username_input.clear()
            password_input.clear()
            refresh_table()
        else:
            QMessageBox.warning(widget, "Lỗi", msg)

    def handle_delete(username):
        confirm = QMessageBox.question(widget, "Xác nhận", f"Xoá người dùng '{username}'?")
        if confirm == QMessageBox.Yes:
            delete_user(username)
            refresh_table()

    add_btn.clicked.connect(handle_add)
    refresh_table()
    return widget
