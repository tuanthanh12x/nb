from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QLineEdit, QFormLayout, QTextEdit,
    QComboBox, QFrame, QGridLayout, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QToolBar, QAction, QColorDialog,
    QDialog, QDialogButtonBox
)
from PyQt5.QtGui import (
    QTextCharFormat, QFont, QIcon, QColor, QTextCursor, QTextListFormat
)
from PyQt5.QtCore import Qt, QDate, QSize
import qtawesome as qta
from functools import partial
from db.db import get_conn
from PyQt5.QtWidgets import QDateEdit

# ===================================================================
# SECTION 0: CUSTOM WIDGETS (WIDGET TÙY CHỈNH)
# ===================================================================

class RichTextEditor(QWidget):
    """
    Một Widget soạn thảo văn bản hiện đại với thanh công cụ định dạng.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        layout.addWidget(self.toolbar)

        self.editor = QTextEdit()
        self.editor.setMinimumHeight(150)
        layout.addWidget(self.editor)

        self._add_actions()
        self.editor.currentCharFormatChanged.connect(self._update_format_buttons)
        self.editor.cursorPositionChanged.connect(self._update_format_buttons)

    def _add_actions(self):
        self.action_bold = self._create_action("fa5s.bold", "In đậm (Ctrl+B)", True, self.toggle_bold)
        self.action_italic = self._create_action("fa5s.italic", "In nghiêng (Ctrl+I)", True, self.toggle_italic)
        self.action_underline = self._create_action("fa5s.underline", "Gạch chân (Ctrl+U)", True, self.toggle_underline)
        self.toolbar.addActions([self.action_bold, self.action_italic, self.action_underline])
        self.toolbar.addSeparator()

        self.action_align_left = self._create_action("fa5s.align-left", "Căn trái", True, lambda: self.editor.setAlignment(Qt.AlignLeft))
        self.action_align_center = self._create_action("fa5s.align-center", "Căn giữa", True, lambda: self.editor.setAlignment(Qt.AlignCenter))
        self.action_align_right = self._create_action("fa5s.align-right", "Căn phải", True, lambda: self.editor.setAlignment(Qt.AlignRight))
        self.action_align_justify = self._create_action("fa5s.align-justify", "Căn đều", True, lambda: self.editor.setAlignment(Qt.AlignJustify))
        self.toolbar.addActions([self.action_align_left, self.action_align_center, self.action_align_right, self.action_align_justify])
        self.toolbar.addSeparator()

        self.action_bullet_list = self._create_action("fa5s.list-ul", "Danh sách (gạch đầu dòng)", False, self.insert_bullet_list)
        self.action_number_list = self._create_action("fa5s.list-ol", "Danh sách (số thứ tự)", False, self.insert_number_list)
        self.toolbar.addActions([self.action_bullet_list, self.action_number_list])
        self.toolbar.addSeparator()

        self.style_combo = QComboBox()
        self.style_combo.setFixedWidth(150)
        self.style_combo.addItems(["Văn bản thường", "Tiêu đề 1", "Tiêu đề 2", "Tiêu đề 3"])
        self.style_combo.activated.connect(self.set_text_style)
        self.toolbar.addWidget(self.style_combo)

    def _create_action(self, icon_name, tooltip, is_checkable, slot):
        action = QAction(qta.icon(icon_name), tooltip, self)
        action.setStatusTip(tooltip)
        action.setCheckable(is_checkable)
        action.triggered.connect(slot)
        return action

    def toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.action_bold.isChecked() else QFont.Normal)
        self.merge_format_on_selection(fmt)

    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.action_italic.isChecked())
        self.merge_format_on_selection(fmt)

    def toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.action_underline.isChecked())
        self.merge_format_on_selection(fmt)

    def insert_list(self, style):
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        list_format = QTextListFormat()
        list_format.setStyle(style)
        cursor.createList(list_format)
        cursor.endEditBlock()

    def insert_bullet_list(self):
        self.insert_list(QTextListFormat.ListDisc)

    def insert_number_list(self):
        self.insert_list(QTextListFormat.ListDecimal)

    def set_text_style(self, index):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()
        if index == 0:
            fmt.setFontPointSize(12)
            fmt.setFontWeight(QFont.Normal)
        elif index == 1:
            fmt.setFontPointSize(20)
            fmt.setFontWeight(QFont.Bold)
        elif index == 2:
            fmt.setFontPointSize(16)
            fmt.setFontWeight(QFont.Bold)
        elif index == 3:
            fmt.setFontPointSize(14)
            fmt.setFontWeight(QFont.Bold)
        self.merge_format_on_selection(fmt)

    def merge_format_on_selection(self, format):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.editor.mergeCurrentCharFormat(format)

    def _update_format_buttons(self):
        fmt = self.editor.currentCharFormat()
        self.action_bold.setChecked(fmt.fontWeight() == QFont.Bold)
        self.action_italic.setChecked(fmt.fontItalic())
        self.action_underline.setChecked(fmt.fontUnderline())
        align = self.editor.alignment()
        self.action_align_left.setChecked(align == Qt.AlignLeft)
        self.action_align_center.setChecked(align == Qt.AlignCenter)
        self.action_align_right.setChecked(align == Qt.AlignRight)
        self.action_align_justify.setChecked(align == Qt.AlignJustify)

    def toHtml(self): return self.editor.toHtml()
    def setHtml(self, html_content): self.editor.setHtml(html_content)
    def toPlainText(self): return self.editor.toPlainText()
    def clear(self): self.editor.clear()
    def setPlaceholderText(self, text): self.editor.setPlaceholderText(text)


# ===================================================================
# SECTION 1: CÁC HÀM TẠO GIAO DIỆN (UI CREATION FUNCTIONS)
# ===================================================================

def create_document_creation_page(main_window, page_id, title_text):
    """
    Tạo trang để cấp số văn bản (Mật hoặc Thường).
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
        ('trich_yeu', "Trích yếu nội dung:", RichTextEditor),
        ('do_mat', "Độ Mật:", QComboBox),
        ('lanh_dao_ky', "Lãnh đạo ký:", QComboBox),
        ('don_vi_soan_thao', "Đơn vị soạn thảo:", QComboBox),
        ('noi_nhan', "Nơi nhận:", QLineEdit),
        ('so_luong_ban', "Số lượng bản:", QLineEdit),
        ('don_vi_luu_tru', "Đơn vị lưu trữ :", QListWidget),
    ]

    for name, label, widget_class in form_fields_config:
        if name == 'do_mat' and page_id != 'mat':
            continue
        widget = widget_class()
        if isinstance(widget, RichTextEditor):
            widget.setPlaceholderText("Nhập trích yếu nội dung văn bản. Sử dụng thanh công cụ để định dạng...")
        elif isinstance(widget, QLineEdit):
            widget.setPlaceholderText(f"Nhập {label.lower().replace(':', '')}...")
        elif isinstance(widget, QListWidget):
            widget.setSelectionMode(QListWidget.ExtendedSelection)
            widget.setMinimumHeight(100)
        elif isinstance(widget, QComboBox):
            if name == 'noi_nhan':
                widget.setEditable(True)
        widgets[name] = widget
        form_layout.addRow(label, widget)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    submit_btn = QPushButton("  Lấy số văn bản")
    submit_btn.setObjectName("submitButton")
    submit_btn.setIcon(qta.icon("fa5s.check", color="white"))
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

    # MỚI: Bố cục cho tiêu đề và nút Tải lại
    title_layout = QHBoxLayout()
    title = QLabel("Sổ quản lý Văn bản 📒")
    title.setObjectName("h2")
    title_layout.addWidget(title)
    title_layout.addStretch()

    reload_button = QPushButton(qta.icon("fa5s.sync-alt"), " Tải lại")
    reload_button.setToolTip("Tải lại danh sách văn bản từ cơ sở dữ liệu")
    title_layout.addWidget(reload_button)
    export_excel_button = QPushButton(qta.icon("fa5s.file-excel", color="green"), " Xuất Excel")
    export_excel_button.setToolTip("Xuất kết quả tìm kiếm ra Excel")
    title_layout.addWidget(export_excel_button)

    export_pdf_button = QPushButton(qta.icon("fa5s.file-pdf", color="red"), " Xuất PDF")
    export_pdf_button.setToolTip("Xuất kết quả tìm kiếm ra PDF")
    title_layout.addWidget(export_pdf_button)
    export_excel_button.clicked.connect(lambda: export_to_excel(main_window))
    export_pdf_button.clicked.connect(lambda: export_to_pdf(main_window))

    layout.addLayout(title_layout)

    # Khung chứa bộ lọc
    filter_frame = QFrame()
    filter_frame.setObjectName("formCard")
    filter_layout = QGridLayout(filter_frame)

    main_window.log_filter_from_date = QDateEdit()
    main_window.log_filter_from_date.setCalendarPopup(True)
    main_window.log_filter_from_date.setDisplayFormat("dd/MM/yyyy")
    main_window.log_filter_from_date.setDate(QDate.currentDate().addMonths(-1))  # mặc định 1 tháng trước

    main_window.log_filter_to_date = QDateEdit()
    main_window.log_filter_to_date.setCalendarPopup(True)
    main_window.log_filter_to_date.setDisplayFormat("dd/MM/yyyy")
    main_window.log_filter_to_date.setDate(QDate.currentDate())  # mặc định hôm nay

    filter_layout.addWidget(QLabel("Từ ngày:"), 3, 0)
    filter_layout.addWidget(main_window.log_filter_from_date, 3, 1)
    filter_layout.addWidget(QLabel("Đến ngày:"), 3, 2)
    filter_layout.addWidget(main_window.log_filter_to_date, 3, 3)


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

    # Bảng dữ liệu
    main_window.log_table = QTableWidget()
    headers = ["ID", "Số VB", "Ngày ban hành", "Loại VB", "Trích yếu", "Lãnh đạo ký", "ĐV Soạn thảo", "Độ mật",
               "Trạng thái", "Hành động"]
    main_window.log_table.setColumnCount(len(headers))
    main_window.log_table.setHorizontalHeaderLabels(headers)
    main_window.log_table.setColumnHidden(0, True)
    main_window.log_table.setColumnHidden(4, True)
    main_window.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
    main_window.log_table.setSelectionBehavior(QTableWidget.SelectRows)
    main_window.log_table.setSelectionMode(QTableWidget.SingleSelection)
    main_window.log_table.verticalHeader().setVisible(False)
    main_window.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    main_window.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    main_window.log_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)
    layout.addWidget(main_window.log_table)

    # Kết nối tín hiệu
    filter_button.clicked.connect(partial(_load_documents_to_log, main_window))
    clear_button.clicked.connect(partial(_clear_filters, main_window))
    main_window.log_search_input.returnPressed.connect(partial(_load_documents_to_log, main_window))
    reload_button.clicked.connect(partial(_load_documents_to_log, main_window)) # MỚI: kết nối nút tải lại
    return page


# ===================================================================
# SECTION 2: CÁC HÀM LOGIC VÀ XỬ LÝ DỮ LIỆU
# ===================================================================

def setup_document_management_logic(main_window):
    _populate_form_combos(main_window)
    _populate_filter_combos(main_window)
    _load_documents_to_log(main_window)

def _populate_form_combos(main_window):
    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                db_map = {
                    'loai_van_ban': "SELECT id, ten FROM loai_van_ban ORDER BY ten",
                    'do_mat': "SELECT id, ten FROM do_mat ORDER BY id",
                    'lanh_dao': "SELECT id, ten FROM lanh_dao ORDER BY ten",
                    'don_vi': "SELECT id, ten FROM don_vi ORDER BY ten",
                    'noi_nhan': "SELECT id, ten FROM noi_nhan ORDER BY ten",
                }
                for page_id in ['mat', 'thuong']:
                    if page_id not in main_window.form_widgets: continue
                    widgets = main_window.form_widgets[page_id]['widgets']
                    widget_query_map = {
                        'loai_van_ban': (db_map['loai_van_ban'], "--- Chọn loại văn bản ---"),
                        'do_mat': (db_map['do_mat'], "--- Chọn độ mật ---"),
                        'lanh_dao_ky': (db_map['lanh_dao'], "--- Chọn lãnh đạo ---"),
                        'don_vi_soan_thao': (db_map['don_vi'], "--- Chọn đơn vị soạn thảo ---"),
                        'don_vi_luu_tru': (db_map['don_vi'], None),
                        'noi_nhan': (db_map['noi_nhan'], ""),
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

def _populate_filter_combos(main_window):
    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                main_window.log_filter_type_combo.addItem("Tất cả loại VB", -1)
                cursor.execute("SELECT id, ten FROM loai_van_ban ORDER BY ten")
                for doc_id, ten in cursor.fetchall(): main_window.log_filter_type_combo.addItem(ten, doc_id)
                main_window.log_filter_unit_combo.addItem("Tất cả đơn vị", -1)
                cursor.execute("SELECT id, ten FROM don_vi ORDER BY ten")
                for unit_id, ten in cursor.fetchall(): main_window.log_filter_unit_combo.addItem(ten, unit_id)
    except Exception as e:
        QMessageBox.critical(main_window, "Lỗi Database", f"Không thể tải dữ liệu cho bộ lọc:\n{e}")

def _validate_form(main_window, page_id):
    widgets = main_window.form_widgets[page_id]['widgets']
    field_display_names = {'loai_van_ban': 'Loại văn bản', 'trich_yeu': 'Trích yếu nội dung', 'do_mat': 'Độ Mật','lanh_dao_ky': 'Lãnh đạo ký', 'don_vi_soan_thao': 'Đơn vị soạn thảo','noi_nhan': 'Nơi nhận', 'don_vi_luu_tru': 'Đơn vị lưu trữ',}
    for name, widget in widgets.items():
        if name in ['so_luong_ban'] or (name == 'do_mat' and page_id != 'mat'): continue
        is_empty = False
        if isinstance(widget, RichTextEditor):
            if not widget.toPlainText().strip(): is_empty = True
        elif isinstance(widget, QLineEdit):
            if not widget.text().strip(): is_empty = True
        elif isinstance(widget, QComboBox):
            if widget.currentData() == -1: is_empty = True
        elif isinstance(widget, QListWidget):
            if not widget.selectedItems(): is_empty = True
        if is_empty:
            field_name = field_display_names.get(name, name)
            return False, f"Vui lòng điền hoặc chọn thông tin cho mục:\n\n'{field_name}'"
    return True, None
def _submit_document(main_window, page_id):
    is_valid, error_message = _validate_form(main_window, page_id)
    if not is_valid:
        QMessageBox.warning(main_window, "Thiếu thông tin", error_message)
        return

    widgets = main_window.form_widgets[page_id]['widgets']
    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                # ==== 1. Sinh số văn bản ====
                current_year = QDate.currentDate().year()
                cursor.execute("SELECT ma_viet_tat FROM loai_van_ban WHERE id = %s",
                               (widgets['loai_van_ban'].currentData(),))
                doc_type_code = cursor.fetchone()[0]

                ngay_thang_nam = QDate.currentDate().toString("dd/MM/yyyy")
                don_vi_soan_thao_id = widgets['don_vi_soan_thao'].currentData()
                cursor.execute("SELECT ten FROM don_vi WHERE id = %s", (don_vi_soan_thao_id,))
                unit_code = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM documents WHERE EXTRACT(YEAR FROM ngay_ban_hanh) = %s",
                               (current_year,))
                so_hien_tai = cursor.fetchone()[0] + 1

                so_van_ban = f"{so_hien_tai:03d}/{doc_type_code}-PA03-{unit_code} ngày {ngay_thang_nam}"

                # ==== 2. Xử lý nơi nhận (sẽ lưu vào documents.don_vi_luu_tru_id) ====
                noi_nhan_text = widgets['noi_nhan'].text().strip()
                noi_nhan_id = None
                if noi_nhan_text:
                    cursor.execute("INSERT INTO noi_nhan (ten) VALUES (%s) RETURNING id", (noi_nhan_text,))
                    noi_nhan_id = cursor.fetchone()[0]

                # ==== 3. Insert vào documents (don_vi_luu_tru_id = nơi nhận) ====
                data = {
                    'loai_so': page_id,
                    'so_van_ban': so_van_ban,
                    'ngay_ban_hanh': QDate.currentDate().toPyDate(),
                    'trich_yeu': widgets['trich_yeu'].toHtml(),
                    'loai_van_ban_id': widgets['loai_van_ban'].currentData(),
                    'do_mat_id': widgets['do_mat'].currentData() if page_id == 'mat' else None,
                    'lanh_dao_id': widgets['lanh_dao_ky'].currentData(),
                    'don_vi_soan_thao_id': don_vi_soan_thao_id,
                    'so_luong_ban': int(widgets['so_luong_ban'].text()) if widgets['so_luong_ban'].text().isdigit() else None,
                    'don_vi_luu_tru_id': noi_nhan_id
                }

                insert_query = """
                    INSERT INTO documents (
                        loai_so, so_van_ban, ngay_ban_hanh, trich_yeu,
                        loai_van_ban_id, do_mat_id, lanh_dao_id,
                        don_vi_soan_thao_id, so_luong_ban, don_vi_luu_tru_id
                    )
                    VALUES (
                        %(loai_so)s, %(so_van_ban)s, %(ngay_ban_hanh)s, %(trich_yeu)s,
                        %(loai_van_ban_id)s, %(do_mat_id)s, %(lanh_dao_id)s,
                        %(don_vi_soan_thao_id)s, %(so_luong_ban)s, %(don_vi_luu_tru_id)s
                    )
                    RETURNING id;
                """
                cursor.execute(insert_query, data)
                new_document_id = cursor.fetchone()[0]

                # ==== 4. Lấy danh sách Đơn vị lưu trữ (giờ sẽ lưu trong document_noi_nhan) ====
                selected_luu_tru_items = widgets['don_vi_luu_tru'].selectedItems()
                don_vi_luu_tru_ids = [item.data(Qt.UserRole) for item in selected_luu_tru_items]

                if don_vi_luu_tru_ids:
                    args_str = ",".join(
                        cursor.mogrify("(%s, %s)", (new_document_id, did)).decode("utf-8")
                        for did in don_vi_luu_tru_ids
                    )
                    cursor.execute(
                        "INSERT INTO document_noi_nhan (document_id, noi_nhan_id) VALUES " + args_str
                    )

                # ==== 5. Cập nhật giao diện ====
                result_label = main_window.form_widgets[page_id]['result_label']
                result_label.setText(f"Cấp số thành công: {so_van_ban}")

                # Reset form
                for widget in widgets.values():
                    if isinstance(widget, (QLineEdit, QTextEdit, RichTextEditor)):
                        widget.clear()
                    elif isinstance(widget, QComboBox):
                        widget.setCurrentIndex(0)
                    elif isinstance(widget, QListWidget):
                        widget.clearSelection()

                _load_documents_to_log(main_window)
                update_document_stats(main_window)

    except Exception as e:
        QMessageBox.critical(main_window, "Lỗi khi cấp số", f"Đã xảy ra lỗi:\n{e}")

def _show_document_content_dialog(parent_window, html_content, document_number):
    dialog = QDialog(parent_window)
    dialog.setWindowTitle(f"Nội dung văn bản: {document_number}")
    dialog.setMinimumSize(700, 500)
    layout = QVBoxLayout(dialog)
    text_viewer = QTextEdit()
    text_viewer.setReadOnly(True)
    text_viewer.setHtml(html_content)
    layout.addWidget(text_viewer)
    button_box = QDialogButtonBox(QDialogButtonBox.Ok)
    button_box.accepted.connect(dialog.accept)
    layout.addWidget(button_box)
    dialog.exec_()


def _load_documents_to_log(main_window):
    if main_window.log_table is None: return
    try:
        search_term = main_window.log_search_input.text().strip()
        type_id = main_window.log_filter_type_combo.currentData()
        unit_id = main_window.log_filter_unit_combo.currentData()
        status_filter = main_window.log_filter_status_combo.currentText()  # Đổi tên biến để rõ ràng hơn

        with get_conn() as conn:
            with conn.cursor() as cursor:
                base_query = """
                             SELECT d.id, \
                                    d.so_van_ban, \
                                    d.ngay_ban_hanh, \
                                    lvb.ten as loai_van_ban,
                                    d.trich_yeu, \
                                    ld.ten  as lanh_dao, \
                                    dv.ten  as don_vi,
                                    dm.ten  as do_mat, \
                                    d.trang_thai
                             FROM documents d
                                      LEFT JOIN loai_van_ban lvb ON d.loai_van_ban_id = lvb.id
                                      LEFT JOIN lanh_dao ld ON d.lanh_dao_id = ld.id
                                      LEFT JOIN don_vi dv ON d.don_vi_soan_thao_id = dv.id
                                      LEFT JOIN do_mat dm ON d.do_mat_id = dm.id \
                             """
                conditions, params = [], []

                if search_term:
                    conditions.append("(d.so_van_ban ILIKE %s OR d.trich_yeu ILIKE %s)")
                    params.extend([f"%{search_term}%", f"%{search_term}%"])
                if type_id != -1:
                    conditions.append("d.loai_van_ban_id = %s")
                    params.append(type_id)
                if unit_id != -1:
                    conditions.append("d.don_vi_soan_thao_id = %s")
                    params.append(unit_id)
                # Sửa logic lọc trạng thái để dùng giá trị từ CSDL
                if status_filter != "Tất cả trạng thái":
                    conditions.append("d.trang_thai = %s")
                    params.append(status_filter)
                from_date = main_window.log_filter_from_date.date().toPyDate()
                to_date = main_window.log_filter_to_date.date().toPyDate()

                if from_date:
                    conditions.append("d.ngay_ban_hanh >= %s")
                    params.append(from_date)
                if to_date:
                    conditions.append("d.ngay_ban_hanh <= %s")
                    params.append(to_date)
                if conditions: base_query += " WHERE " + " AND ".join(conditions)
                base_query += " ORDER BY d.ngay_ban_hanh DESC, d.id DESC"

                cursor.execute(base_query, tuple(params))
                records = cursor.fetchall()
                main_window.log_table.setRowCount(0)

                for row_index, row_data in enumerate(records):
                    main_window.log_table.insertRow(row_index)

                    document_id, document_number, trich_yeu_html, document_status = row_data[0], row_data[1], row_data[
                        4], row_data[8]
                    is_pending = (document_status == 'Chờ xác nhận')

                    # --- BẮT ĐẦU PHẦN TÔ MÀU ---
                    row_color = QColor("red") if is_pending else QColor(Qt.black)
                    for col_index, col_data in enumerate(row_data):
                        if col_index in [4, 9]: continue  # Bỏ qua cột trích yếu và cột hành động
                        item = QTableWidgetItem(str(col_data) if col_data is not None else "")
                        item.setForeground(row_color)  # Đặt màu cho chữ
                        main_window.log_table.setItem(row_index, col_index, item)
                    # --- KẾT THÚC PHẦN TÔ MÀU ---

                    # --- BẮT ĐẦU PHẦN THÊM NÚT HÀNH ĐỘNG ---
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 0, 5, 0)
                    action_layout.setSpacing(5)
                    action_layout.setAlignment(Qt.AlignCenter)

                    # Nút Xem (luôn hiển thị)
                    view_button = QPushButton(qta.icon("fa5s.eye", color='#007bff'), " Xem")
                    view_button.setCursor(Qt.PointingHandCursor)
                    view_button.setToolTip("Xem trích yếu nội dung")
                    view_button.clicked.connect(
                        partial(_show_document_content_dialog, main_window, trich_yeu_html, document_number))
                    action_layout.addWidget(view_button)

                    # Nút Xác nhận và Hủy (chỉ hiển thị khi chờ xác nhận)
                    if is_pending:
                        confirm_button = QPushButton(qta.icon("fa5s.check-circle", color='green'), " Xác nhận")
                        confirm_button.setCursor(Qt.PointingHandCursor)
                        confirm_button.setToolTip("Chuyển trạng thái sang 'Đã xác nhận'")
                        confirm_button.clicked.connect(
                            partial(_update_document_status, main_window, document_id, 'Đã xác nhận'))
                        action_layout.addWidget(confirm_button)

                        cancel_button = QPushButton(qta.icon("fa5s.times-circle", color='red'), " Hủy")
                        cancel_button.setCursor(Qt.PointingHandCursor)
                        cancel_button.setToolTip("Chuyển trạng thái sang 'Đã hủy'")
                        cancel_button.clicked.connect(
                            partial(_update_document_status, main_window, document_id, 'Đã hủy'))
                        action_layout.addWidget(cancel_button)

                    main_window.log_table.setCellWidget(row_index, 9, action_widget)
                    # --- KẾT THÚC PHẦN THÊM NÚT HÀNH ĐỘNG ---

    except Exception as e:
        QMessageBox.critical(main_window, "Lỗi Database", f"Không thể tải danh sách văn bản:\n{e}")

def _clear_filters(main_window):
    main_window.log_search_input.clear()
    main_window.log_filter_type_combo.setCurrentIndex(0)
    main_window.log_filter_unit_combo.setCurrentIndex(0)
    main_window.log_filter_status_combo.setCurrentIndex(0)
    _load_documents_to_log(main_window)

def update_document_stats(main_window):
    if main_window.current_user_role != "Admin" or main_window.total_docs_label is None: return
    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM documents")
                total = cursor.fetchone()[0]
                cursor.execute("SELECT trang_thai, COUNT(*) FROM documents GROUP BY trang_thai")
                stats = dict(cursor.fetchall())
                confirmed = stats.get('Đã xác nhận', 0)
                pending = stats.get('Chờ xác nhận', 0)
                canceled = stats.get('Đã hủy', 0)
                main_window.total_docs_label.setText(str(total))
                main_window.confirmed_docs_label.setText(str(confirmed))
                main_window.pending_docs_label.setText(str(pending))
                main_window.canceled_docs_label.setText(str(canceled))
    except Exception as e:
        print(f"Lỗi khi cập nhật thống kê: {e}")


def _update_document_status(main_window, document_id, new_status):
    """
    Hàm để cập nhật trạng thái của văn bản trong CSDL.
    Hiển thị hộp thoại xác nhận trước khi thực hiện.
    """
    action_verb = "xác nhận" if new_status == "Đã xác nhận" else "hủy"
    question_msg = f"Bạn có chắc chắn muốn {action_verb} văn bản có ID {document_id} không?"

    reply = QMessageBox.question(main_window, f"Xác nhận hành động", question_msg,
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    if reply == QMessageBox.Yes:
        try:
            with get_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE documents SET trang_thai = %s WHERE id = %s", (new_status, document_id))

            QMessageBox.information(main_window, "Thành công", f"Đã {action_verb} văn bản thành công.")

            # Tải lại danh sách và cập nhật thống kê để hiển thị thay đổi
            _load_documents_to_log(main_window)
            update_document_stats(main_window)

        except Exception as e:
            QMessageBox.critical(main_window, "Lỗi Database", f"Không thể cập nhật trạng thái văn bản:\n{e}")



import openpyxl
from openpyxl.styles import Font, Alignment
from PyQt5.QtWidgets import QFileDialog

def export_to_excel(main_window):
    row_count = main_window.log_table.rowCount()
    col_count = main_window.log_table.columnCount()

    if row_count == 0:
        QMessageBox.warning(main_window, "Xuất Excel", "Không có dữ liệu để xuất!")
        return

    path, _ = QFileDialog.getSaveFileName(main_window, "Lưu file Excel", "", "Excel Files (*.xlsx)")
    if not path: return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh sách VB"

    # Header
    headers = [main_window.log_table.horizontalHeaderItem(c).text() for c in range(col_count) if not main_window.log_table.isColumnHidden(c)]
    ws.append(headers)

    for col in ws.iter_cols(min_row=1, max_row=1):
        for cell in col:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

    # Data
    for r in range(row_count):
        row_data = []
        for c in range(col_count):
            if not main_window.log_table.isColumnHidden(c):
                item = main_window.log_table.item(r, c)
                row_data.append(item.text() if item else "")
        ws.append(row_data)

    wb.save(path)
    QMessageBox.information(main_window, "Xuất Excel", f"Xuất dữ liệu thành công:\n{path}")


from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

def export_to_pdf(main_window):
    row_count = main_window.log_table.rowCount()
    col_count = main_window.log_table.columnCount()

    if row_count == 0:
        QMessageBox.warning(main_window, "Xuất PDF", "Không có dữ liệu để xuất!")
        return

    path, _ = QFileDialog.getSaveFileName(main_window, "Lưu file PDF", "", "PDF Files (*.pdf)")
    if not path: return

    data = []
    headers = [main_window.log_table.horizontalHeaderItem(c).text() for c in range(col_count) if not main_window.log_table.isColumnHidden(c)]
    data.append(headers)

    for r in range(row_count):
        row_data = []
        for c in range(col_count):
            if not main_window.log_table.isColumnHidden(c):
                item = main_window.log_table.item(r, c)
                row_data.append(item.text() if item else "")
        data.append(row_data)

    pdf = SimpleDocTemplate(path, pagesize=A4)
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    pdf.build([table])
    QMessageBox.information(main_window, "Xuất PDF", f"Xuất dữ liệu thành công:\n{path}")
