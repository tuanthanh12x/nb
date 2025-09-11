from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QLineEdit, QFormLayout, QTextEdit,
    QComboBox, QFrame, QGridLayout, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QToolBar, QAction,
    QDialog, QDialogButtonBox, QAbstractItemView, QFileDialog, QDateEdit
)
from PyQt5.QtGui import (
    QTextCharFormat, QFont, QColor, QTextCursor, QTextListFormat
)
from PyQt5.QtCore import Qt, QDate, QSize
import qtawesome as qta
from functools import partial
from db.db import get_conn

# ===================================================================
# SECTION 0: CUSTOM WIDGETS (WIDGET TÙY CHỈNH)
# ===================================================================
class DocumentDetailDialog(QDialog):
    def __init__(self, parent, document_id):
        super().__init__(parent)
        self.setWindowTitle("Chi tiết văn bản")
        self.setMinimumSize(900, 640)
        self.document_id = document_id
        self.init_ui()
        self.load_lookups()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.widgets = {
            'so_van_ban': QLineEdit(),
            'ngay_ban_hanh': QDateEdit(),
            'trich_yeu': RichTextEditor(),
            'lanh_dao_id': QComboBox(),
            'don_vi_soan_thao_id': QComboBox(),
            'can_bo_soan_thao': QLineEdit(),      # <<< MỚI
            'noi_nhan': QLineEdit(),              # map với documents.noinhanx
            'so_luong_ban': QLineEdit(),
            'trang_thai': QComboBox()
        }
        self.widgets['ngay_ban_hanh'].setCalendarPopup(True)
        self.widgets['ngay_ban_hanh'].setDisplayFormat("dd/MM/yyyy")
        self.widgets['trang_thai'].addItems(["Chờ xác nhận", "Đã xác nhận", "Đã hủy"])

        for label, widget in self.widgets.items():
            form.addRow(label.replace("_", " ").title(), widget)
        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.save_changes)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def load_lookups(self):
        """Nạp dữ liệu cho các combobox trước khi setCurrentIndex/findData."""
        try:
            with get_conn() as conn:
                with conn.cursor() as cursor:
                    # lãnh đạo
                    cursor.execute("SELECT id, ten FROM lanh_dao ORDER BY ten")
                    self.widgets['lanh_dao_id'].clear()
                    for _id, ten in cursor.fetchall():
                        self.widgets['lanh_dao_id'].addItem(ten, _id)

                    # đơn vị soạn thảo
                    cursor.execute("SELECT id, ten FROM don_vi ORDER BY ten")
                    self.widgets['don_vi_soan_thao_id'].clear()
                    for _id, ten in cursor.fetchall():
                        self.widgets['don_vi_soan_thao_id'].addItem(ten, _id)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh mục:\n{e}")

    def load_data(self):
        try:
            with get_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT so_van_ban, ngay_ban_hanh, trich_yeu, lanh_dao_id,
                               don_vi_soan_thao_id, can_bo_soan_thao, so_luong_ban, trang_thai, noinhanx
                        FROM documents WHERE id = %s
                    """, (self.document_id,))
                    row = cursor.fetchone()
                    if not row:
                        QMessageBox.warning(self, "Thông báo", "Không tìm thấy văn bản.")
                        self.reject()
                        return

                    #       0           1              2           3
                    #       4           5                 6            7           8
                    # don_vi_id, can_bo_st, so_luong, trang_thai, noi_nhan
                    so_van_ban, ngay, trich_yeu, lanh_dao_id, don_vi_id, can_bo_st, so_luong, trang_thai, noi_nhan = row

                    self.widgets['so_van_ban'].setText(so_van_ban or "")
                    if ngay:
                        self.widgets['ngay_ban_hanh'].setDate(QDate(ngay.year, ngay.month, ngay.day))
                    self.widgets['trich_yeu'].setHtml(trich_yeu or "")

                    # setCurrentIndex bằng findData (sau khi combobox đã có dữ liệu)
                    ld_idx = self.widgets['lanh_dao_id'].findData(lanh_dao_id)
                    if ld_idx >= 0:
                        self.widgets['lanh_dao_id'].setCurrentIndex(ld_idx)

                    dv_idx = self.widgets['don_vi_soan_thao_id'].findData(don_vi_id)
                    if dv_idx >= 0:
                        self.widgets['don_vi_soan_thao_id'].setCurrentIndex(dv_idx)

                    self.widgets['can_bo_soan_thao'].setText(can_bo_st or "")

                    self.widgets['so_luong_ban'].setText("" if so_luong is None else str(so_luong))
                    if trang_thai:
                        self.widgets['trang_thai'].setCurrentText(trang_thai)
                    self.widgets['noi_nhan'].setText(noi_nhan or "")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu:\n{e}")

    def save_changes(self):
        data = {
            'so_van_ban': self.widgets['so_van_ban'].text().strip(),
            'ngay_ban_hanh': self.widgets['ngay_ban_hanh'].date().toPyDate(),
            'trich_yeu': self.widgets['trich_yeu'].toHtml(),
            'lanh_dao_id': self.widgets['lanh_dao_id'].currentData(),
            'don_vi_soan_thao_id': self.widgets['don_vi_soan_thao_id'].currentData(),
            'can_bo_soan_thao': self.widgets['can_bo_soan_thao'].text().strip(),  # <<< MỚI
            'so_luong_ban': (self.widgets['so_luong_ban'].text().strip() or None),
            'trang_thai': self.widgets['trang_thai'].currentText(),
            'noinhanx': self.widgets['noi_nhan'].text().strip(),
            'id': self.document_id
        }
        # ép kiểu số lượng
        if data['so_luong_ban'] is not None and not data['so_luong_ban'].isdigit():
            QMessageBox.warning(self, "Dữ liệu không hợp lệ", "Số lượng bản phải là số.")
            return
        if data['so_luong_ban'] is not None:
            data['so_luong_ban'] = int(data['so_luong_ban'])

        try:
            with get_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE documents
                           SET so_van_ban=%(so_van_ban)s,
                               ngay_ban_hanh=%(ngay_ban_hanh)s,
                               trich_yeu=%(trich_yeu)s,
                               lanh_dao_id=%(lanh_dao_id)s,
                               don_vi_soan_thao_id=%(don_vi_soan_thao_id)s,
                               can_bo_soan_thao=%(can_bo_soan_thao)s,
                               so_luong_ban=%(so_luong_ban)s,
                               trang_thai=%(trang_thai)s,
                               noinhanx=%(noinhanx)s
                         WHERE id=%(id)s
                    """, data)
            QMessageBox.information(self, "Thành công", "Đã cập nhật văn bản.")
            self.accept()  # để caller biết và reload
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật văn bản:\n{e}")


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
        ('can_bo_soan_thao', "Cán bộ soạn thảo:", QLineEdit),  # <<< MỚI
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

    # Tiêu đề + nút
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

    # Bộ lọc
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
    headers = [
        "ID", "Số VB", "Ngày ban hành", "Loại VB", "Trích yếu", "Lãnh đạo ký",
        "ĐV Soạn thảo", "Cán Bộ Soạn Thảo", "Độ mật", "Trạng thái", "Nơi nhận", "Hành động"
    ]
    main_window.log_table.setColumnCount(len(headers))
    main_window.log_table.setHorizontalHeaderLabels(headers)

    # Ẩn cột không cần nhìn trực tiếp
    main_window.log_table.setColumnHidden(0, True)  # ID
    main_window.log_table.setColumnHidden(4, True)  # Trích yếu (đã có nút Xem)

    # Chế độ chọn + hiển thị
    main_window.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
    main_window.log_table.setSelectionBehavior(QTableWidget.SelectRows)
    main_window.log_table.setSelectionMode(QTableWidget.SingleSelection)
    main_window.log_table.setAlternatingRowColors(True)
    main_window.log_table.setWordWrap(False)
    main_window.log_table.verticalHeader().setVisible(False)

    # Cấu hình header theo cột (tránh ResizeToContents toàn cục)
    header = main_window.log_table.horizontalHeader()
    header.setStretchLastSection(False)

    # Mặc định: cho phép người dùng kéo resize
    for i in range(len(headers)):
        header.setSectionResizeMode(i, QHeaderView.Interactive)

    # Cột co giãn chính: "Nơi nhận" (index 10)
    header.setSectionResizeMode(10, QHeaderView.Stretch)

    # Cột “Hành động” (index 11)
    header.setSectionResizeMode(11, QHeaderView.Fixed)
    main_window.log_table.setColumnWidth(11, 220)

    # Các cột còn lại đặt width hợp lý
    preset_widths = {
        1: 200,  # Số VB
        2: 130,  # Ngày ban hành
        3: 150,  # Loại VB
        5: 160,  # Lãnh đạo ký
        6: 180,  # ĐV Soạn thảo
        7: 180,  # Cán bộ Soạn thảo
        8: 100,  # Độ mật
        9: 130,  # Trạng thái
    }
    for col, w in preset_widths.items():
        main_window.log_table.setColumnWidth(col, w)

    # Tránh cuộn theo từng “mảng lớn”
    main_window.log_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
    main_window.log_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

    layout.addWidget(main_window.log_table)

    # Kết nối tín hiệu
    filter_button.clicked.connect(partial(_load_documents_to_log, main_window))
    clear_button.clicked.connect(partial(_clear_filters, main_window))
    main_window.log_search_input.returnPressed.connect(partial(_load_documents_to_log, main_window))
    reload_button.clicked.connect(partial(_load_documents_to_log, main_window))
    return page


# ===================================================================
# SECTION 2: CÁC HÀM LOGIC VÀ XỬ LÝ DỮ LIỆU
# ===================================================================

def setup_document_management_logic(main_window):
    _populate_form_combos(main_window)
    _populate_filter_combos(main_window)
    _load_documents_to_log(main_window)

    def _on_row_dbl_clicked(r, c):
        id_item = main_window.log_table.item(r, 0)  # cột 0 = ID (đang hidden)
        if id_item:
            try:
                doc_id = int(id_item.text())
                open_document_detail(main_window, doc_id)
            except ValueError:
                pass

    main_window.log_table.cellDoubleClicked.connect(_on_row_dbl_clicked)


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
                    if page_id not in main_window.form_widgets:
                        continue
                    widgets = main_window.form_widgets[page_id]['widgets']
                    widget_query_map = {
                        'loai_van_ban': (db_map['loai_van_ban'], "--- Chọn loại văn bản ---"),
                        'do_mat': (db_map['do_mat'], "--- Chọn độ mật ---"),
                        'lanh_dao_ky': (db_map['lanh_dao'], "--- Chọn lãnh đạo ---"),
                        'don_vi_soan_thao': (db_map['don_vi'], "--- Chọn đơn vị soạn thảo ---"),
                        'don_vi_luu_tru': (db_map['don_vi'], None)
                    }
                    for name, widget in widgets.items():
                        if name in widget_query_map:
                            query, placeholder = widget_query_map[name]
                            cursor.execute(query)
                            records = cursor.fetchall()
                            widget.clear()
                            if isinstance(widget, QComboBox):
                                if placeholder:
                                    widget.addItem(placeholder, -1)
                                for db_id, db_ten in records:
                                    widget.addItem(db_ten, db_id)
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
                for doc_id, ten in cursor.fetchall():
                    main_window.log_filter_type_combo.addItem(ten, doc_id)

                main_window.log_filter_unit_combo.addItem("Tất cả đơn vị", -1)
                cursor.execute("SELECT id, ten FROM don_vi ORDER BY ten")
                for unit_id, ten in cursor.fetchall():
                    main_window.log_filter_unit_combo.addItem(ten, unit_id)
    except Exception as e:
        QMessageBox.critical(main_window, "Lỗi Database", f"Không thể tải dữ liệu cho bộ lọc:\n{e}")


def _validate_form(main_window, page_id):
    widgets = main_window.form_widgets[page_id]['widgets']
    field_display_names = {
        'loai_van_ban': 'Loại văn bản',
        'trich_yeu': 'Trích yếu nội dung',
        'do_mat': 'Độ Mật',
        'lanh_dao_ky': 'Lãnh đạo ký',
        'don_vi_soan_thao': 'Đơn vị soạn thảo',
        'noi_nhan': 'Nơi nhận',
        'don_vi_luu_tru': 'Đơn vị lưu trữ',
    }
    for name, widget in widgets.items():
        if name in ['so_luong_ban'] or (name == 'do_mat' and page_id != 'mat'):
            continue
        is_empty = False
        if isinstance(widget, RichTextEditor):
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
                # ==== 1. Sinh số văn bản (theo loại VB + theo năm) ====
                current_year = QDate.currentDate().year()
                loai_so = page_id  # 'mat' hoặc 'thuong'
                # lấy mã viết tắt loại văn bản (VD: BC, TM, …)
                loai_vb_id = widgets['loai_van_ban'].currentData()
                cursor.execute("SELECT ma_viet_tat FROM loai_van_ban WHERE id = %s", (loai_vb_id,))
                doc_type_code = (cursor.fetchone() or [""])[0] or ""
                doc_type_code = doc_type_code.upper()

                ngay_thang_nam = QDate.currentDate().toString("dd/MM/yyyy")

                # đơn vị soạn thảo để ghép đuôi
                don_vi_soan_thao_id = widgets['don_vi_soan_thao'].currentData()
                cursor.execute("SELECT ten FROM don_vi WHERE id = %s", (don_vi_soan_thao_id,))
                unit_code = (cursor.fetchone() or [""])[0] or ""

                # ĐẾM SỐ HIỆN TẠI CHO RIÊNG LOẠI VĂN BẢN (và theo năm)
                cursor.execute("""
                    SELECT MAX(CAST(regexp_replace(split_part(d.so_van_ban, '/', 1), '\D', '', 'g') AS INT))
                    FROM documents d
                    WHERE d.loai_van_ban_id = %s
                                AND d.loai_so = %s           

                      AND EXTRACT(YEAR FROM d.ngay_ban_hanh) = %s
                """, (loai_vb_id, current_year))
                max_so = cursor.fetchone()[0]
                so_moi = (max_so or 0) + 1

                if doc_type_code == "CV":
                    # Công văn: không thêm code
                    so_van_ban = f"{so_moi:03d}/PA03-{unit_code} ngày {ngay_thang_nam}"
                else:
                    # Các loại khác: có code
                    so_van_ban = f"{so_moi:03d}/{doc_type_code}-PA03-{unit_code} ngày {ngay_thang_nam}"

                # ==== 2. Xử lý nơi nhận (sẽ lưu vào documents.don_vi_luu_tru_id) ====
                noi_nhan_text = widgets['noi_nhan'].text().strip()
                noi_nhan_id = None
                if noi_nhan_text:
                    cursor.execute("INSERT INTO noi_nhan (ten) VALUES (%s) RETURNING id", (noi_nhan_text,))
                    noi_nhan_id = cursor.fetchone()[0]

                # ==== 3. Insert vào documents ====
                data = {
                    'loai_so': page_id,
                    'so_van_ban': so_van_ban,
                    'ngay_ban_hanh': QDate.currentDate().toPyDate(),
                    'trich_yeu': widgets['trich_yeu'].toHtml(),
                    'loai_van_ban_id': widgets['loai_van_ban'].currentData(),
                    'do_mat_id': widgets['do_mat'].currentData() if page_id == 'mat' else None,
                    'lanh_dao_id': widgets['lanh_dao_ky'].currentData(),
                    'don_vi_soan_thao_id': don_vi_soan_thao_id,
                    'can_bo_soan_thao': widgets['can_bo_soan_thao'].text().strip(),  # <<< MỚI
                    'so_luong_ban': int(widgets['so_luong_ban'].text()) if widgets['so_luong_ban'].text().isdigit() else None,
                    'don_vi_luu_tru_id': noi_nhan_id,
                    'noinhanx': noi_nhan_text,
                }

                insert_query = """
                    INSERT INTO documents (
                        loai_so, so_van_ban, ngay_ban_hanh, trich_yeu,
                        loai_van_ban_id, do_mat_id, lanh_dao_id,
                        don_vi_soan_thao_id, can_bo_soan_thao,
                        so_luong_ban, noinhanx
                    )
                    VALUES (
                        %(loai_so)s, %(so_van_ban)s, %(ngay_ban_hanh)s, %(trich_yeu)s,
                        %(loai_van_ban_id)s, %(do_mat_id)s, %(lanh_dao_id)s,
                        %(don_vi_soan_thao_id)s, %(can_bo_soan_thao)s,
                        %(so_luong_ban)s, %(noinhanx)s
                    )
                    RETURNING id;
                """
                cursor.execute(insert_query, data)
                new_document_id = cursor.fetchone()[0]

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
    if main_window.log_table is None:
        return
    try:
        search_term = main_window.log_search_input.text().strip()
        type_id = main_window.log_filter_type_combo.currentData()
        unit_id = main_window.log_filter_unit_combo.currentData()
        status_filter = main_window.log_filter_status_combo.currentText()

        with get_conn() as conn:
            with conn.cursor() as cursor:
                base_query = """
                    SELECT d.id,
                           d.so_van_ban,
                           d.ngay_ban_hanh,
                           lvb.ten AS loai_van_ban,
                           d.trich_yeu,
                           ld.ten  AS lanh_dao,
                           dv.ten  AS don_vi,
                           d.can_bo_soan_thao,
                           dm.ten  AS do_mat,
                           d.trang_thai,
                           d.noinhanx
                    FROM documents d
                    LEFT JOIN loai_van_ban lvb ON d.loai_van_ban_id = lvb.id
                    LEFT JOIN lanh_dao     ld  ON d.lanh_dao_id      = ld.id
                    LEFT JOIN don_vi       dv  ON d.don_vi_soan_thao_id = dv.id
                    LEFT JOIN do_mat       dm  ON d.do_mat_id        = dm.id
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

                if conditions:
                    base_query += " WHERE " + " AND ".join(conditions)
                base_query += " ORDER BY d.ngay_ban_hanh DESC, d.id DESC"

                cursor.execute(base_query, tuple(params))
                records = cursor.fetchall()
                main_window.log_table.setRowCount(0)

                for row_index, row_data in enumerate(records):
                    main_window.log_table.insertRow(row_index)

                    # row_data indices:
                    # 0 ID, 1 Số VB, 2 Ngày, 3 Loại, 4 Trích yếu, 5 Lãnh đạo,
                    # 6 ĐV soạn thảo, 7 Cán bộ soạn thảo, 8 Độ mật, 9 Trạng thái, 10 Nơi nhận
                    document_id = row_data[0]
                    document_number = row_data[1]
                    trich_yeu_html = row_data[4]
                    status_raw = row_data[9] or ''  # đúng index trạng thái

                    # Normalize trạng thái chờ
                    status_norm = (status_raw or '').strip().casefold()
                    pending_variants = {
                        'chờ xác nhận', 'cho xac nhan', 'cho xác nhận', 'chờ xác nhận'
                    }
                    pending_variants = {s.casefold() for s in pending_variants}
                    is_pending = status_norm in pending_variants

                    # Tô màu hàng theo trạng thái
                    row_color = QColor("red") if is_pending else QColor(Qt.black)

                    for col_index, col_data in enumerate(row_data):
                        # bỏ qua cột Trích yếu (4) vì xem qua nút
                        if col_index in [4]:
                            continue
                        item = QTableWidgetItem(str(col_data) if col_data is not None else "")
                        item.setForeground(row_color)
                        main_window.log_table.setItem(row_index, col_index, item)

                    # Widget hành động đặt ở cột 11 (sau “Nơi nhận”)
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 0, 5, 0)
                    action_layout.setSpacing(5)
                    action_layout.setAlignment(Qt.AlignCenter)

                    view_button = QPushButton(qta.icon("fa5s.eye", color='#007bff'), " Xem")
                    view_button.setCursor(Qt.PointingHandCursor)
                    view_button.setToolTip("Xem trích yếu nội dung")
                    view_button.clicked.connect(
                        partial(_show_document_content_dialog, main_window, trich_yeu_html, document_number)
                    )
                    action_layout.addWidget(view_button)

                    edit_button = QPushButton(qta.icon("fa5s.edit", color='#17a2b8'), " Sửa")
                    edit_button.setCursor(Qt.PointingHandCursor)
                    edit_button.setToolTip("Mở chi tiết để chỉnh sửa")
                    edit_button.clicked.connect(partial(open_document_detail, main_window, document_id))
                    action_layout.addWidget(edit_button)

                    # XÓA (hard delete)
                    delete_button = QPushButton(qta.icon("fa5s.trash-alt", color='crimson'), " Xóa")
                    delete_button.setCursor(Qt.PointingHandCursor)
                    delete_button.setToolTip("Xóa vĩnh viễn văn bản khỏi hệ thống")
                    delete_button.clicked.connect(partial(_delete_document, main_window, document_id))
                    action_layout.addWidget(delete_button)

                    if is_pending:
                        confirm_button = QPushButton(qta.icon("fa5s.check-circle", color='green'), " Xác nhận")
                        confirm_button.setCursor(Qt.PointingHandCursor)
                        confirm_button.setToolTip("Chuyển trạng thái sang 'Đã xác nhận'")
                        confirm_button.clicked.connect(
                            partial(_update_document_status, main_window, document_id, 'Đã xác nhận')
                        )
                        action_layout.addWidget(confirm_button)

                        cancel_button = QPushButton(qta.icon("fa5s.times-circle", color='red'), " Hủy")
                        cancel_button.setCursor(Qt.PointingHandCursor)
                        cancel_button.setToolTip("Chuyển trạng thái sang 'Đã hủy'")
                        cancel_button.clicked.connect(
                            partial(_update_document_status, main_window, document_id, 'Đã hủy')
                        )
                        action_layout.addWidget(cancel_button)

                    main_window.log_table.setCellWidget(row_index, 11, action_widget)

    except Exception as e:
        QMessageBox.critical(main_window, "Lỗi Database", f"Không thể tải danh sách văn bản:\n{e}")


def _clear_filters(main_window):
    main_window.log_search_input.clear()
    main_window.log_filter_type_combo.setCurrentIndex(0)
    main_window.log_filter_unit_combo.setCurrentIndex(0)
    main_window.log_filter_status_combo.setCurrentIndex(0)
    _load_documents_to_log(main_window)


def open_document_detail(main_window, document_id: int):
    dlg = DocumentDetailDialog(main_window, document_id)
    if dlg.exec_() == QDialog.Accepted:
        # reload bảng & thống kê sau khi lưu
        _load_documents_to_log(main_window)
        update_document_stats(main_window)


def update_document_stats(main_window):
    if getattr(main_window, "current_user_role", None) != "Admin" or getattr(main_window, "total_docs_label", None) is None:
        return
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

    reply = QMessageBox.question(main_window, "Xác nhận hành động", question_msg,
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


def _delete_document(main_window, document_id: int):
    """
    Xóa vĩnh viễn 1 văn bản theo ID.
    LƯU Ý: Nếu có quan hệ phụ thuộc (ví dụ document_noi_nhan),
    nên cấu hình FK ON DELETE CASCADE hoặc xóa dữ liệu con trước.
    """
    reply = QMessageBox.question(
        main_window,
        "Xóa văn bản",
        f"Bạn có chắc muốn xóa vĩnh viễn văn bản ID {document_id} không?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    if reply != QMessageBox.Yes:
        return

    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        QMessageBox.information(main_window, "Thành công", "Đã xóa văn bản.")
        _load_documents_to_log(main_window)
        update_document_stats(main_window)
    except Exception as e:
        QMessageBox.critical(main_window, "Lỗi Database", f"Không thể xóa văn bản:\n{e}")


# ===================================================================
# EXPORTS
# ===================================================================
import openpyxl
from openpyxl.styles import Font, Alignment
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

def export_to_excel(main_window):
    row_count = main_window.log_table.rowCount()
    col_count = main_window.log_table.columnCount()

    if row_count == 0:
        QMessageBox.warning(main_window, "Xuất Excel", "Không có dữ liệu để xuất!")
        return

    path, _ = QFileDialog.getSaveFileName(main_window, "Lưu file Excel", "", "Excel Files (*.xlsx)")
    if not path:
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh sách VB"

    # Header
    headers = [main_window.log_table.horizontalHeaderItem(c).text()
               for c in range(col_count) if not main_window.log_table.isColumnHidden(c)]
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


def export_to_pdf(main_window):
    row_count = main_window.log_table.rowCount()
    col_count = main_window.log_table.columnCount()

    if row_count == 0:
        QMessageBox.warning(main_window, "Xuất PDF", "Không có dữ liệu để xuất!")
        return

    path, _ = QFileDialog.getSaveFileName(main_window, "Lưu file PDF", "", "PDF Files (*.pdf)")
    if not path:
        return

    data = []
    headers = [main_window.log_table.horizontalHeaderItem(c).text()
               for c in range(col_count) if not main_window.log_table.isColumnHidden(c)]
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
