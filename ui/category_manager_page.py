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
    # (Tên bảng DB, Tên hiển thị, Tên cột chính, [Tên cột phụ])
    categories = [
        ("don_vi", "Đơn vị", ["id", "ten"]),
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

    # Tải dữ liệu cho panel đầu tiên
    if len(categories) > 0:
        on_category_changed(0)

    return page


def _create_management_panel(table_name, display_name, column_headers):
    # (Hàm này và các hàm bên dưới là nội bộ của file này, không cần export)
    # ... (Nội dung hàm giữ nguyên như cũ)
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setSpacing(15)

    button_layout = QHBoxLayout()
    add_btn = QPushButton("  Thêm mới");
    add_btn.setIcon(qta.icon("fa5s.plus", color="white"));
    add_btn.setObjectName("submitButton")
    edit_btn = QPushButton("  Sửa");
    edit_btn.setIcon(qta.icon("fa5s.edit", color="white"));
    edit_btn.setEnabled(False)
    delete_btn = QPushButton("  Xóa");
    delete_btn.setIcon(qta.icon("fa5s.trash-alt", color="white"));
    delete_btn.setObjectName("dangerButton");
    delete_btn.setEnabled(False)

    button_layout.addWidget(add_btn);
    button_layout.addWidget(edit_btn);
    button_layout.addWidget(delete_btn);
    button_layout.addStretch()
    layout.addLayout(button_layout)

    table = QTableWidget()
    table.setColumnCount(len(column_headers));
    table.setHorizontalHeaderLabels(column_headers)
    table.setEditTriggers(QTableWidget.NoEditTriggers);
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection);
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setColumnHidden(0, True)
    layout.addWidget(table)

    table.itemSelectionChanged.connect(lambda: _update_button_state(table, edit_btn, delete_btn))
    add_btn.clicked.connect(lambda: _add_item(table, table_name, column_headers))
    edit_btn.clicked.connect(lambda: _edit_item(table, table_name, column_headers))
    delete_btn.clicked.connect(lambda: _delete_item(table, table_name))

    return panel


def _load_data_to_table(table_widget, table_name, columns):
    # ... (Nội dung hàm giữ nguyên như cũ)
    try:
        conn = get_conn()
        cursor = conn.cursor()
        column_names = [f'"{c}"' for c in columns]  # Handle potential keywords
        cursor.execute(f"SELECT {', '.join(column_names)} FROM {table_name} ORDER BY id ASC")
        records = cursor.fetchall()
        table_widget.setRowCount(0)
        for row_index, row_data in enumerate(records):
            table_widget.insertRow(row_index)
            for col_index, col_data in enumerate(row_data):
                table_widget.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Database", f"Không thể tải dữ liệu từ bảng '{table_name}':\n{e}")
    finally:
        if conn: conn.close()


def _update_button_state(table, edit_btn, delete_btn):
    # ... (Nội dung hàm giữ nguyên như cũ)
    is_selected = bool(table.selectedItems())
    edit_btn.setEnabled(is_selected);
    delete_btn.setEnabled(is_selected)


def _add_item(table, table_name, columns):
    # ... (Nội dung hàm giữ nguyên như cũ)
    fields_to_input = columns[1:]
    values = []
    for field in fields_to_input:
        value, ok = QInputDialog.getText(None, f"Thêm {table_name}", f"Nhập {field}:")
        if not ok: return
        if not value.strip() and 'ma_viet_tat' not in field:
            QMessageBox.warning(None, "Dữ liệu không hợp lệ", f"{field} không được để trống.");
            return
        values.append(value.strip())
    try:
        conn = get_conn()
        cursor = conn.cursor()
        query = f"INSERT INTO {table_name} ({', '.join(fields_to_input)}) VALUES ({', '.join(['%s'] * len(values))})"
        cursor.execute(query, tuple(values));
        conn.commit()
        QMessageBox.information(None, "Thành công", "Đã thêm mục mới thành công!")
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Database", f"Không thể thêm mục mới:\n{e}")
    finally:
        if conn: conn.close()
        _load_data_to_table(table, table_name, columns)


def _edit_item(table, table_name, columns):
    # ... (Nội dung hàm giữ nguyên như cũ)
    selected_row = table.currentRow()
    if selected_row < 0: return
    item_id = table.item(selected_row, 0).text()
    fields_to_edit = columns[1:]
    new_values = []
    for i, field in enumerate(fields_to_edit):
        current_value = table.item(selected_row, i + 1).text()
        new_value, ok = QInputDialog.getText(None, f"Sửa {table_name}", f"Nhập {field} mới:", text=current_value)
        if not ok: return
        if not new_value.strip() and 'ma_viet_tat' not in field:
            QMessageBox.warning(None, "Dữ liệu không hợp lệ", f"{field} không được để trống.");
            return
        new_values.append(new_value.strip())
    try:
        conn = get_conn()
        cursor = conn.cursor()
        set_clause = ", ".join([f"{field} = %s" for field in fields_to_edit])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        cursor.execute(query, tuple(new_values) + (item_id,));
        conn.commit()
        QMessageBox.information(None, "Thành công", "Đã cập nhật mục thành công!")
    except Exception as e:
        QMessageBox.critical(None, "Lỗi Database", f"Không thể cập nhật mục:\n{e}")
    finally:
        if conn: conn.close()
        _load_data_to_table(table, table_name, columns)


def _delete_item(table, table_name):
    # ... (Nội dung hàm giữ nguyên như cũ)
    selected_row = table.currentRow()
    if selected_row < 0: return
    item_id = table.item(selected_row, 0).text()
    item_name = table.item(selected_row, 1).text()
    reply = QMessageBox.question(None, "Xác nhận xóa",
                                 f"Bạn có chắc chắn muốn xóa mục:\n'{item_name}' (ID: {item_id})?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (item_id,));
            conn.commit()
            QMessageBox.information(None, "Thành công", "Đã xóa mục thành công!")
        except Exception as e:
            QMessageBox.critical(None, "Lỗi Database",
                                 f"Không thể xóa mục. Có thể mục này đang được sử dụng ở nơi khác.\nLỗi: {e}")
        finally:
            if conn: conn.close()
            columns = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
            _load_data_to_table(table, table_name, columns)