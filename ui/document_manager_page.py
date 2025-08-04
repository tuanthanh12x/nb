# ui/document_manager_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QLineEdit, QFormLayout, QTextEdit,
    QComboBox, QFrame, QGridLayout, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QDate
import qtawesome as qta
from functools import partial
from db.db import get_conn


# ===================================================================
# SECTION 1: CÁC HÀM TẠO GIAO DIỆN (UI CREATION FUNCTIONS)
# ===================================================================

def create_document_creation_page(main_window, page_id, title_text):
    """
    Tạo trang để cấp số văn bản (Mật hoặc Thường).
    Hàm này chỉ tạo giao diện, không chứa logic.
    """
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(30, 20, 30, 30)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignTop)

    title = QLabel(title_text)
    title.setObjectName("h2")
    layout.addWidget(title)

    result_label = QLabel("")
    result_label.setObjectName("resultLabel")
    result_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(result_label)

    form_card = QFrame()
    form_card.setObjectName("formCard")
    form_layout = QFormLayout(form_card)
    form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
    layout.addWidget(form_card)

    widgets = {}
    main_window.form_widgets[page_id] = {'widgets': widgets, 'result_label': result_label}

    form_fields_config = [
        ('loai_van_ban', "Loại văn bản:", QComboBox),
        ('trich_yeu', "Trích yếu nội dung:", QTextEdit),
        ('do_mat', "Độ Mật:", QComboBox),
        ('lanh_dao_ky', "Lãnh đạo ký:", QComboBox),
        ('don_vi_soan_thao', "Đơn vị soạn thảo:", QComboBox),
        ('noi_nhan', "Nơi nhận (chọn nhiều):", QListWidget),
        ('so_luong_ban', "Số lượng bản:", QLineEdit),
        ('don_vi_luu_tru', "Đơn vị lưu trữ:", QComboBox),
    ]

    for name, label, widget_class in form_fields_config:
        if name == 'do_mat' and page_id != 'mat':
            continue

        widget = widget_class()
        if isinstance(widget, QTextEdit):
            widget.setPlaceholderText("Nhập trích yếu nội dung văn bản...")
            widget.setMinimumHeight(80)
        elif isinstance(widget, QLineEdit):
            widget.setPlaceholderText(f"Nhập {label.lower().replace(':', '')}...")
        elif isinstance(widget, QListWidget):
            widget.setSelectionMode(QListWidget.ExtendedSelection)
            widget.setMinimumHeight(100)

        widgets[name] = widget
        form_layout.addRow(label, widget)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    submit_btn = QPushButton("  Lấy số văn bản")
    submit_btn.setObjectName("submitButton")
    submit_btn.setIcon(qta.icon("fa5s.check", color="white"))
    # Kết nối tới hàm logic, truyền vào `main_window` và `page_id`
    # submit_btn.clicked.connect(partial(_submit_document, main_window, page_id))
    # btn_layout.addWidget(submit_btn)
    # layout.addLayout(btn_layout)
    # layout.addStretch()
    # main_window.form_widgets[page_id]['button'] = submit_btn
    # # Kết nối tín hiệu để validate form
    # for name, widget in widgets.items():
    #     if isinstance(widget, (QLineEdit, QTextEdit)):
    #         # Nếu là ô nhập văn bản, lắng nghe sự kiện textChanged
    #         widget.textChanged.connect(partial(_validate_form, main_window, page_id))
    #     elif isinstance(widget, QComboBox):
    #         # Nếu là combobox, lắng nghe sự kiện currentIndexChanged
    #         widget.currentIndexChanged.connect(partial(_validate_form, main_window, page_id))
    #     elif isinstance(widget, QListWidget):
    #         # Nếu là danh sách, lắng nghe sự kiện itemSelectionChanged
    #         widget.itemSelectionChanged.connect(partial(_validate_form, main_window, page_id))
    submit_btn.setEnabled(True)

    submit_btn.clicked.connect(partial(_submit_document, main_window, page_id))
    btn_layout.addWidget(submit_btn)
    layout.addLayout(btn_layout)
    layout.addStretch()

    main_window.form_widgets[page_id]['button'] = submit_btn

    return page


def create_document_log_page(main_window):
    """
    Tạo trang Sổ quản lý văn bản với bộ lọc và bảng dữ liệu.
    """
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(30, 20, 30, 30)
    layout.setSpacing(15)

    title = QLabel("Sổ quản lý Văn bản 📒")
    title.setObjectName("h2")
    layout.addWidget(title)

    filter_frame = QFrame()
    filter_frame.setObjectName("formCard")
    filter_layout = QGridLayout(filter_frame)

    # Gán các widget vào main_window để các hàm khác có thể truy cập
    main_window.log_search_input = QLineEdit()
    main_window.log_search_input.setPlaceholderText("Tìm theo số văn bản, trích yếu...")
    main_window.log_filter_type_combo = QComboBox()
    main_window.log_filter_unit_combo = QComboBox()
    main_window.log_filter_status_combo = QComboBox()
    main_window.log_filter_status_combo.addItems(["Tất cả trạng thái", "Chờ xác nhận", "Đã xác nhận", "Đã hủy"])

    filter_layout.addWidget(QLabel("Tìm kiếm:"), 0, 0)
    filter_layout.addWidget(main_window.log_search_input, 0, 1, 1, 3)
    filter_layout.addWidget(QLabel("Loại VB:"), 1, 0)
    filter_layout.addWidget(main_window.log_filter_type_combo, 1, 1)
    filter_layout.addWidget(QLabel("ĐV Soạn thảo:"), 1, 2)
    filter_layout.addWidget(main_window.log_filter_unit_combo, 1, 3)
    filter_layout.addWidget(QLabel("Trạng thái:"), 1, 4)
    filter_layout.addWidget(main_window.log_filter_status_combo, 1, 5)

    filter_button = QPushButton("  Lọc / Tìm kiếm")
    filter_button.setIcon(qta.icon("fa5s.search", color="white"))
    filter_button.setObjectName("submitButton")

    clear_button = QPushButton("  Xóa bộ lọc")
    clear_button.setIcon(qta.icon("fa5s.times", color="white"))

    filter_layout.addWidget(filter_button, 2, 0, 1, 3)
    filter_layout.addWidget(clear_button, 2, 3, 1, 3)

    layout.addWidget(filter_frame)

    main_window.log_table = QTableWidget()
    headers = ["ID", "Số VB", "Ngày ban hành", "Loại VB", "Trích yếu", "Lãnh đạo ký", "ĐV Soạn thảo", "Độ mật",
               "Trạng thái"]
    main_window.log_table.setColumnCount(len(headers))
    main_window.log_table.setHorizontalHeaderLabels(headers)
    main_window.log_table.setColumnHidden(0, True)
    main_window.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
    main_window.log_table.setSelectionBehavior(QTableWidget.SelectRows)
    main_window.log_table.setSelectionMode(QTableWidget.SingleSelection)
    main_window.log_table.verticalHeader().setVisible(False)
    main_window.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    main_window.log_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

    layout.addWidget(main_window.log_table)

    # Kết nối tín hiệu tới các hàm logic
    filter_button.clicked.connect(partial(_load_documents_to_log, main_window))
    clear_button.clicked.connect(partial(_clear_filters, main_window))
    main_window.log_search_input.returnPressed.connect(partial(_load_documents_to_log, main_window))

    return page


# ===================================================================
# SECTION 2: CÁC HÀM LOGIC VÀ XỬ LÝ DỮ LIỆU
# ===================================================================

def setup_document_management_logic(main_window):
    """
    Hàm tổng hợp để chạy các tác vụ setup ban đầu cho quản lý văn bản.
    Được gọi một lần trong __init__ của ModernApp.
    """
    _populate_form_combos(main_window)
    _populate_filter_combos(main_window)
    _load_documents_to_log(main_window)


def _populate_form_combos(main_window):
    """Tải dữ liệu từ DB vào các ComboBox trên form tạo văn bản."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        db_map = {
            'loai_van_ban': "SELECT id, ten FROM loai_van_ban ORDER BY ten",
            'do_mat': "SELECT id, ten FROM do_mat ORDER BY id",
            'lanh_dao': "SELECT id, ten FROM lanh_dao ORDER BY ten",
            'don_vi': "SELECT id, ten FROM don_vi ORDER BY ten",
            'noi_nhan': "SELECT id, ten FROM noi_nhan ORDER BY ten",
        }

        # Lặp qua cả hai form 'mat' và 'thuong'
        for page_id in ['mat', 'thuong']:
            if page_id not in main_window.form_widgets: continue

            widgets = main_window.form_widgets[page_id]['widgets']
            # Ánh xạ tên widget tới câu lệnh query
            widget_query_map = {
                'loai_van_ban': (db_map['loai_van_ban'], "--- Chọn loại văn bản ---"),
                'do_mat': (db_map['do_mat'], "--- Chọn độ mật ---"),
                'lanh_dao_ky': (db_map['lanh_dao'], "--- Chọn lãnh đạo ---"),
                'don_vi_soan_thao': (db_map['don_vi'], "--- Chọn đơn vị soạn thảo ---"),
                'don_vi_luu_tru': (db_map['don_vi'], "--- Chọn đơn vị lưu trữ ---"),
                'noi_nhan': (db_map['noi_nhan'], None),
            }

            for name, widget in widgets.items():
                if name in widget_query_map:
                    query, placeholder = widget_query_map[name]
                    cursor.execute(query)
                    records = cursor.fetchall()

                    widget.clear()
                    if isinstance(widget, QComboBox):
                        if placeholder: widget.addItem(placeholder, -1)
                        for db_id, db_ten in records: widget.addItem(db_ten, db_id)
                    elif isinstance(widget, QListWidget):
                        for db_id, db_ten in records:
                            item = QListWidgetItem(db_ten)
                            item.setData(Qt.UserRole, db_id)
                            widget.addItem(item)
    except Exception as e:
        QMessageBox.critical(main_window, "Lỗi Database", f"Không thể tải dữ liệu cho form:\n{e}")
    finally:
        if conn: conn.close()


def _populate_filter_combos(main_window):
    """Lấy dữ liệu từ DB để điền vào các ComboBox lọc trên trang sổ quản lý."""
    try:
        conn = get_conn()
        cursor = conn.cursor()

        # Loại văn bản
        main_window.log_filter_type_combo.addItem("Tất cả loại VB", -1)
        cursor.execute("SELECT id, ten FROM loai_van_ban ORDER BY ten")
        for doc_id, ten in cursor.fetchall(): main_window.log_filter_type_combo.addItem(ten, doc_id)

        # Đơn vị soạn thảo
        main_window.log_filter_unit_combo.addItem("Tất cả đơn vị", -1)
        cursor.execute("SELECT id, ten FROM don_vi ORDER BY ten")
        for unit_id, ten in cursor.fetchall(): main_window.log_filter_unit_combo.addItem(ten, unit_id)

    except Exception as e:
        QMessageBox.critical(main_window, "Lỗi Database", f"Không thể tải dữ liệu cho bộ lọc:\n{e}")
    finally:
        if conn: conn.close()


def _validate_form(main_window, page_id):
    """
    Kiểm tra xem các trường bắt buộc đã được điền chưa.
    Trả về một tuple: (is_valid, error_message).
    """
    widgets = main_window.form_widgets[page_id]['widgets']

    # Ánh xạ tên nội bộ của widget sang tên hiển thị cho người dùng
    field_display_names = {
        'loai_van_ban': 'Loại văn bản',
        'trich_yeu': 'Trích yếu nội dung',
        'do_mat': 'Độ Mật',
        'lanh_dao_ky': 'Lãnh đạo ký',
        'don_vi_soan_thao': 'Đơn vị soạn thảo',
        'noi_nhan': 'Nơi nhận',
        'don_vi_luu_tru': 'Đơn vị lưu trữ',
    }

    # Lặp qua các widget để tìm lỗi ĐẦU TIÊN
    for name, widget in widgets.items():
        # Bỏ qua các trường không bắt buộc
        if name in ['so_luong_ban']:
            continue
        # Bỏ qua trường độ mật nếu là văn bản thường
        if name == 'do_mat' and page_id != 'mat':
            continue

        is_empty = False
        if isinstance(widget, QTextEdit):
            if not widget.toPlainText().strip():
                is_empty = True
        elif isinstance(widget, QLineEdit):
            if not widget.text().strip():
                is_empty = True
        elif isinstance(widget, QComboBox):
            if widget.currentData() == -1:
                is_empty = True
        elif isinstance(widget, QListWidget):
            if not widget.selectedItems():
                is_empty = True

        # Nếu tìm thấy một trường rỗng, trả về lỗi ngay lập tức
        if is_empty:
            field_name = field_display_names.get(name, name)
            error_message = f"Vui lòng điền hoặc chọn thông tin cho mục:\n\n'{field_name}'"
            return (False, error_message)

    # Nếu không tìm thấy lỗi nào, trả về thành công
    return (True, None)


def _submit_document(main_window, page_id):
    """Thu thập dữ liệu, sinh số văn bản và ghi vào database."""
    is_valid, error_message = _validate_form(main_window, page_id)
    if not is_valid:
        # Nếu không hợp lệ, hiển thị cảnh báo và dừng hàm tại đây
        QMessageBox.warning(main_window, "Thiếu thông tin", error_message)
        return
    widgets = main_window.form_widgets[page_id]['widgets']
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        current_year = QDate.currentDate().year()
        cursor.execute("SELECT ma_viet_tat FROM loai_van_ban WHERE id = %s", (widgets['loai_van_ban'].currentData(),))
        doc_type_code = cursor.fetchone()[0]

        # Cần lấy tên đơn vị từ CSDL hoặc cấu hình
        don_vi_soan_thao_id = widgets['don_vi_soan_thao'].currentData()
        cursor.execute("SELECT ma_viet_tat FROM don_vi WHERE id = %s", (don_vi_soan_thao_id,))
        unit_code = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM documents WHERE EXTRACT(YEAR FROM ngay_ban_hanh) = %s", (current_year,))
        so_hien_tai = cursor.fetchone()[0] + 1
        so_van_ban = f"{so_hien_tai:03d}/{doc_type_code}-{unit_code}"

        data = {
            'loai_so': page_id,
            'so_van_ban': so_van_ban,
            'ngay_ban_hanh': QDate.currentDate().toPyDate(),
            'trich_yeu': widgets['trich_yeu'].toPlainText().strip(),
            'loai_van_ban_id': widgets['loai_van_ban'].currentData(),
            'do_mat_id': widgets['do_mat'].currentData() if page_id == 'mat' else None,
            'lanh_dao_id': widgets['lanh_dao_ky'].currentData(),
            'don_vi_soan_thao_id': don_vi_soan_thao_id,
            'so_luong_ban': int(widgets['so_luong_ban'].text()) if widgets['so_luong_ban'].text().isdigit() else None,
            'don_vi_luu_tru_id': widgets['don_vi_luu_tru'].currentData(),
        }

        insert_query = """
                       INSERT INTO documents (loai_so, so_van_ban, ngay_ban_hanh, trich_yeu, loai_van_ban_id,
                                              do_mat_id, lanh_dao_id, don_vi_soan_thao_id, so_luong_ban,
                                              don_vi_luu_tru_id)
                       VALUES (%(loai_so)s, %(so_van_ban)s, %(ngay_ban_hanh)s, %(trich_yeu)s, %(loai_van_ban_id)s,
                               %(do_mat_id)s, %(lanh_dao_id)s, %(don_vi_soan_thao_id)s, %(so_luong_ban)s,
                               %(don_vi_luu_tru_id)s) RETURNING id; \
                       """
        cursor.execute(insert_query, data)
        new_document_id = cursor.fetchone()[0]

        selected_noi_nhan_items = widgets['noi_nhan'].selectedItems()
        noi_nhan_ids = [item.data(Qt.UserRole) for item in selected_noi_nhan_items]
        if noi_nhan_ids:
            args_str = ','.join(
                cursor.mogrify("(%s,%s)", (new_document_id, nid)).decode('utf-8') for nid in noi_nhan_ids)
            cursor.execute("INSERT INTO document_noi_nhan (document_id, noi_nhan_id) VALUES " + args_str)

        conn.commit()

        result_label = main_window.form_widgets[page_id]['result_label']
        ngay_thang_nam = QDate.currentDate().toString("dd/MM/yyyy")
        result_label.setText(f"Cấp số thành công: {so_van_ban} ngày {ngay_thang_nam}")

        for widget in widgets.values():
            if isinstance(widget, (QLineEdit, QTextEdit)):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QListWidget):
                widget.clearSelection()

        _load_documents_to_log(main_window)
        update_document_stats(main_window)

    except Exception as e:
        if conn: conn.rollback()
        QMessageBox.critical(main_window, "Lỗi khi cấp số", f"Đã xảy ra lỗi:\n{e}")
    finally:
        if conn: conn.close()


def _load_documents_to_log(main_window):
    """Tải/Tải lại dữ liệu văn bản vào bảng dựa trên các tiêu chí lọc."""
    if main_window.log_table is None: return  # Chưa khởi tạo bảng thì bỏ qua
    try:
        search_term = main_window.log_search_input.text().strip()
        type_id = main_window.log_filter_type_combo.currentData()
        unit_id = main_window.log_filter_unit_combo.currentData()
        status = main_window.log_filter_status_combo.currentText()

        conn = get_conn()
        cursor = conn.cursor()

        base_query = """
                     SELECT d.id, \
                            d.so_van_ban, \
                            d.ngay_ban_hanh, \
                            lvb.ten as loai_van_ban, \
                            d.trich_yeu,
                            ld.ten  as lanh_dao, \
                            dv.ten  as don_vi, \
                            dm.ten  as do_mat, \
                            d.trang_thai
                     FROM documents d
                              LEFT JOIN loai_van_ban lvb ON d.loai_van_ban_id = lvb.id
                              LEFT JOIN lanh_dao ld ON d.lanh_dao_id = ld.id
                              LEFT JOIN don_vi dv ON d.don_vi_soan_thao_id = dv.id
                              LEFT JOIN do_mat dm ON d.do_mat_id = dm.id \
                     """
        conditions = []
        params = []

        if search_term:
            conditions.append("(d.so_van_ban ILIKE %s OR d.trich_yeu ILIKE %s)")
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        if type_id != -1:
            conditions.append("d.loai_van_ban_id = %s")
            params.append(type_id)
        if unit_id != -1:
            conditions.append("d.don_vi_soan_thao_id = %s")
            params.append(unit_id)
        if status != "Tất cả trạng thái":
            conditions.append("d.trang_thai = %s")
            params.append(status)

        if conditions: base_query += " WHERE " + " AND ".join(conditions)
        base_query += " ORDER BY d.ngay_ban_hanh DESC, d.id DESC"

        cursor.execute(base_query, tuple(params))
        records = cursor.fetchall()

        main_window.log_table.setRowCount(0)
        for row_index, row_data in enumerate(records):
            main_window.log_table.insertRow(row_index)
            for col_index, col_data in enumerate(row_data):
                item_text = str(col_data) if col_data is not None else ""
                item = QTableWidgetItem(item_text)
                main_window.log_table.setItem(row_index, col_index, item)

    except Exception as e:
        QMessageBox.critical(main_window, "Lỗi Database", f"Không thể tải danh sách văn bản:\n{e}")
    finally:
        if conn: conn.close()


def _clear_filters(main_window):
    """Reset các ô lọc và tải lại toàn bộ dữ liệu."""
    main_window.log_search_input.clear()
    main_window.log_filter_type_combo.setCurrentIndex(0)
    main_window.log_filter_unit_combo.setCurrentIndex(0)
    main_window.log_filter_status_combo.setCurrentIndex(0)
    _load_documents_to_log(main_window)


def update_document_stats(main_window):
    """Cập nhật các thẻ thống kê trên trang chủ Admin."""
    if main_window.current_user_role != "Admin" or main_window.total_docs_label is None:
        return

    try:
        conn = get_conn()
        cursor = conn.cursor()

        # Lấy tổng số văn bản
        cursor.execute("SELECT COUNT(*) FROM documents")
        total = cursor.fetchone()[0]

        # Lấy số lượng theo trạng thái
        cursor.execute("SELECT trang_thai, COUNT(*) FROM documents GROUP BY trang_thai")
        stats = dict(cursor.fetchall())

        confirmed = stats.get('Đã xác nhận', 0)
        pending = stats.get('Chờ xác nhận', 0)
        canceled = stats.get('Đã hủy', 0)

        # Cập nhật giao diện
        main_window.total_docs_label.setText(str(total))
        main_window.confirmed_docs_label.setText(str(confirmed))
        main_window.pending_docs_label.setText(str(pending))
        main_window.canceled_docs_label.setText(str(canceled))

    except Exception as e:
        print(f"Lỗi khi cập nhật thống kê: {e}")
    finally:
        if conn: conn.close()