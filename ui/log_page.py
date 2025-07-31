# Trong file ui/log_page.py

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QTableWidget, QHeaderView)
import qtawesome as qta
from .styles import COLORS # Sử dụng relative import

# Đổi tên hàm và thêm tham số main_window
def create_log_page(main_window):
    """
    Tạo trang Sổ quản lý văn bản.
    main_window được truyền vào để gán table widget vào đó.
    """
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(30, 20, 30, 30)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignTop)

    title = QLabel("Sổ Quản lý Văn bản 📖")
    title.setObjectName("h2")
    layout.addWidget(title)

    # Thanh công cụ (tìm kiếm, xuất file)
    toolbar_layout = QHBoxLayout()
    search_input = QLineEdit()
    search_input.setPlaceholderText("Tìm kiếm theo số, nội dung...")
    export_btn = QPushButton("Xuất ra Excel")
    export_btn.setIcon(qta.icon("fa5s.file-excel", color=COLORS["text_dark"]))
    toolbar_layout.addWidget(search_input)
    toolbar_layout.addWidget(export_btn)
    layout.addLayout(toolbar_layout)

    # Bảng hiển thị log
    # Thay 'self' bằng 'main_window'
    main_window.log_table = QTableWidget()
    main_window.log_table.setColumnCount(5)
    main_window.log_table.setHorizontalHeaderLabels(
        ["Số VB", "Ngày ban hành", "Loại VB", "Trích yếu nội dung", "Trạng thái"])
    main_window.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
    main_window.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    main_window.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
    main_window.log_table.setAlternatingRowColors(True)
    layout.addWidget(main_window.log_table)

    return page