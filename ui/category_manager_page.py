# ui/category_manager_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import qtawesome as qta

# Import hàm kết nối DB từ thư mục gốc
from db.db import get_conn


def create_category_management_page():
    """
    Tạo trang giao diện chính để quản lý tất cả các danh mục.
    Đây là hàm duy nhất cần được import từ bên ngoài.
    """
    page = QWidget()
    main_layout = QVBoxLayout(page)
    main_layout.setContentsMargins(30, 20, 30, 30)
    main_layout.setSpacing(20)
    main_layout.setAlignment(Qt.AlignTop)

    title = QLabel("🗂️ Quản lý Danh mục")
    title.setObjectName("h2")
    main_layout.addWidget(title)

    # --- Khu vực chọn danh mục ---
    selector_layout = QHBoxLayout()
    selector_layout.addWidget(QLabel("Chọn danh mục để quản lý:"))

    category_selector = QComboBox()
    main_layout.addLayout(selector_layout)
    main_layout.addWidget(category_selector)

    # --- Khu vực hiển thị các panel quản lý ---
    panels_stack = QStackedWidget()
    main_layout.addWidget(panels_stack)

    # --- Định nghĩa các danh mục cần quản lý ---
    # (Tên bảng DB, Tên hiển thị, [Danh sách tên các cột])
    categories = [
        ("don_vi", "Đơn vị", ["id", "ten", "ma_viet_tat"]),
        ("lanh_dao", "Lãnh đạo", ["id", "ten", "chuc_vu"]),
        ("loai_van_ban", "Loại văn bản", ["id", "ten", "ma_viet_tat"]),
        ("do_mat", "Độ mật", ["id", "ten"]),
        ("noi_nhan", "Nơi nhận", ["id", "ten"])
    ]

    for i, (table_name, display_name, columns) in enumerate(categories):
        panel = _create_management_panel(table_name, display_name, columns)
        panels_stack.addWidget(panel)
        category_selector.addItem(display_name)

    def on_category_changed(index):
        panels_stack.setCurrentIndex(index)
        current_panel = panels_stack.widget(index)
        if current_panel:
            table_widget = current_panel.findChild(QTableWidget)
            table_name = categories[index][0]
            columns = categories[index][2]
            _load_data_to_table(table_widget, table_name, columns)

    category_selector.currentIndexChanged.connect(on_category_changed)

    # Tải dữ liệu cho panel đầu tiên khi khởi động
    if len(categories) > 0:
        on_category_changed(0)

    return page


def _create_management_panel(table_name, display_name, column_headers):
    """Tạo một panel riêng để quản lý một danh mục (thêm/sửa/xóa)."""
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setSpacing(15)

    button_layout = QHBoxLayout()
    add_btn = QPushButton("  Thêm mới")
    add_btn.setIcon(qta.icon("fa5s.plus", color="white"))
    add_btn.setObjectName("submitButton")
    edit_btn = QPushButton("  Sửa")
    edit_btn.setIcon(qta.icon("fa5s.edit", color="white"))
    edit_btn.setEnabled(False)
    delete_btn = QPushButton("  Xóa")
    delete_btn.setIcon(qta.icon("fa5s.trash-alt", color="white"))
    delete_btn.setObjectName("dangerButton")
    delete_btn.setEnabled(False)

    button_layout.addWidget(add_btn)
    button_layout.addWidget(edit_btn)
    button_layout.addWidget(delete_btn)
    button_layout.addStretch()
    layout.addLayout(button_layout)

    table = QTableWidget()
    table.setColumnCount(len(column_headers))
    # Đặt tên cho các cột header
    table.setHorizontalHeaderLabels([h.replace('_', ' ').title() for h in column_headers])
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    # Ẩn cột ID (cột đầu tiên)
    table.setColumnHidden(0, True)
    layout.addWidget(table)

    # Kết nối tín hiệu
    table.itemSelectionChanged.connect(lambda: _update_button_state(table, edit_btn, delete_btn))
    add_btn.clicked.connect(lambda: _add_item(table, table_name, column_headers))
    edit_btn.clicked.connect(lambda: _edit_item(table, table_name, column_headers))
    delete_btn.clicked.connect(lambda: _delete_item(table, table_name))

    return panel


def _load_data_to_table(table_widget, table_name, columns):
    """Tải dữ liệu từ một bảng trong CSDL SQLite vào QTableWidget."""
    try:
        # Sử dụng 'with' để quản lý kết nối an toàn
        with get_conn() as conn:
            cursor = conn.cursor()
            # Câu lệnh SELECT đơn giản, không cần trích dẫn tên cột cho SQLite
            query = f"SELECT {', '.join(columns)} FROM {table_name} ORDER BY id ASC"
            cursor.execute(query)
            records = cursor.fetchall()

            table_widget.setRowCount(0)
            for row_index, row_data in enumerate(records):
                table_widget.insertRow(row_index)
                for col_index, col_data in enumerate(row_data):
                    table_widget.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Database", f"Không thể tải dữ liệu từ bảng '{table_name}':\n{e}")


def _update_button_state(table, edit_btn, delete_btn):
    """Bật/tắt nút Sửa và Xóa dựa trên việc có hàng nào được chọn hay không."""
    is_selected = bool(table.selectedItems())
    edit_btn.setEnabled(is_selected)
    delete_btn.setEnabled(is_selected)


def _add_item(table, table_name, columns):
    """Thêm một mục mới vào bảng được chỉ định."""
    fields_to_input = columns[1:]  # Bỏ qua cột 'id'
    values = []
    for field in fields_to_input:
        display_field_name = field.replace('_', ' ').title()
        value, ok = QInputDialog.getText(None, f"Thêm - {table_name.title()}", f"Nhập {display_field_name}:")
        if not ok: return # Người dùng nhấn Cancel

        # Kiểm tra dữ liệu không được để trống (trừ trường hợp cụ thể nếu có)
        if not value.strip():
            QMessageBox.warning(None, "Dữ liệu không hợp lệ", f"{display_field_name} không được để trống.")
            return
        values.append(value.strip())

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            # Sửa đổi cho SQLite: Dùng '?' làm placeholder
            placeholders = ', '.join(['?'] * len(values))
            query = f"INSERT INTO {table_name} ({', '.join(fields_to_input)}) VALUES ({placeholders})"
            cursor.execute(query, tuple(values))
            conn.commit()
        QMessageBox.information(None, "Thành công", "Đã thêm mục mới thành công!")
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Database", f"Không thể thêm mục mới:\n{e}")
    finally:
        # Tải lại dữ liệu sau khi thao tác
        _load_data_to_table(table, table_name, columns)


def _edit_item(table, table_name, columns):
    """Sửa một mục đã có trong bảng."""
    selected_row = table.currentRow()
    if selected_row < 0: return

    item_id = table.item(selected_row, 0).text()
    fields_to_edit = columns[1:] # Bỏ qua cột 'id'
    new_values = []

    for i, field in enumerate(fields_to_edit):
        current_value = table.item(selected_row, i + 1).text()
        display_field_name = field.replace('_', ' ').title()
        new_value, ok = QInputDialog.getText(None, f"Sửa - {table_name.title()}", f"Nhập {display_field_name} mới:", text=current_value)
        if not ok: return

        if not new_value.strip():
            QMessageBox.warning(None, "Dữ liệu không hợp lệ", f"{display_field_name} không được để trống.")
            return
        new_values.append(new_value.strip())

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            # Sửa đổi cho SQLite: Dùng '?' làm placeholder
            set_clause = ", ".join([f"{field} = ?" for field in fields_to_edit])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
            # Thêm item_id vào cuối tuple dữ liệu
            cursor.execute(query, tuple(new_values) + (item_id,))
            conn.commit()
        QMessageBox.information(None, "Thành công", "Đã cập nhật mục thành công!")
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Database", f"Không thể cập nhật mục:\n{e}")
    finally:
        _load_data_to_table(table, table_name, columns)


def _delete_item(table, table_name):
    """Xóa một mục đã chọn khỏi bảng."""
    selected_row = table.currentRow()
    if selected_row < 0: return

    item_id = table.item(selected_row, 0).text()
    item_name = table.item(selected_row, 1).text() # Giả sử cột thứ 2 luôn là tên chính

    reply = QMessageBox.question(None, "Xác nhận xóa",
                                 f"Bạn có chắc chắn muốn xóa mục:\n'{item_name}' (ID: {item_id})?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    if reply == QMessageBox.Yes:
        try:
            with get_conn() as conn:
                cursor = conn.cursor()
                # Sửa đổi cho SQLite: Dùng '?' làm placeholder
                cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (item_id,))
                conn.commit()
            QMessageBox.information(None, "Thành công", "Đã xóa mục thành công!")
        except Exception as e:
            QMessageBox.critical(None, "Lỗi Database",
                                 f"Không thể xóa mục. Có thể mục này đang được sử dụng ở nơi khác.\nLỗi: {e}")
        finally:
            columns = [table.horizontalHeaderItem(i).text().lower().replace(' ', '_') for i in range(table.columnCount())]
            _load_data_to_table(table, table_name, columns)