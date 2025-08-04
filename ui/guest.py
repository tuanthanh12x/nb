import hashlib
import sys
# Cần cài đặt thư viện: pip install PyQt5 qtawesome
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QListWidget, QListWidgetItem,
    QLineEdit, QFormLayout, QTextEdit, QComboBox, QFrame,
    QGridLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QInputDialog, QTabWidget
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QDate, QSize
import qtawesome as qta
from functools import partial


# Giả lập các module để code có thể chạy độc lập
# --- Bắt đầu phần giả lập ---
class MockDB:
    def get_conn(self):
        return self

    def cursor(self):
        return self

    def execute(self, query, params):
        # Mật khẩu mặc định là 'admin', tên đăng nhập là 'admin'
        hashed_pass = hashlib.sha256('admin'.encode()).hexdigest()
        if params[0] == 'admin' and params[1] == hashed_pass:
            self._result = [('Admin',)]
        else:
            self._result = None

    def fetchone(self):
        return self._result[0] if self._result else None

    def close(self):
        pass


db_mock = MockDB()


def get_conn():
    # Trong môi trường thực tế, bạn sẽ kết nối tới DB thật
    # Ở đây chúng ta dùng mock để demo
    print("Đang kết nối tới DB (mock)...")
    return db_mock


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user_management_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.addWidget(QLabel("Trang Quản lý Người dùng (Placeholder)"))
    return page


COLORS = {
    'primary': '#0F172A',
    'secondary': '#1E293B',
    'background': '#020617',
    'text': '#E2E8F0',
    'text_light': '#94A3B8',
    'accent': '#38BDF8',
    'danger': '#F43F5E',
}


def get_global_stylesheet():
    return f"""
        /* --- General --- */
        QMainWindow, QWidget {{
            background-color: {COLORS['background']};
            color: {COLORS['text']};
            font-family: Segoe UI;
            font-size: 14px;
        }}
        /* --- Headings --- */
        QLabel#h1 {{ font-size: 28px; font-weight: 600; }}
        QLabel#h2 {{ font-size: 22px; font-weight: 600; color: {COLORS['text']}; }}
        /* --- Cards & Frames --- */
        QFrame#statCard, QFrame#formCard {{
            background-color: {COLORS['secondary']};
            border-radius: 8px;
            padding: 15px;
        }}
        QFrame#loginFrame {{
             background-color: {COLORS['secondary']};
             border-radius: 12px;
             max-width: 500px;
        }}
        /* --- Buttons --- */
        QPushButton {{
            background-color: {COLORS['accent']};
            color: {COLORS['primary']};
            font-weight: 600;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
        }}
        QPushButton:hover {{ background-color: #7DD3FC; }}
        QPushButton:pressed {{ background-color: #0EA5E9; }}
        QPushButton#submitButton {{ background-color: #22C55E; color: white; }}
        QPushButton#submitButton:hover {{ background-color: #4ADE80; }}
        QPushButton#submitButton:disabled {{ background-color: #475569; color: #94A3B8; }}
        QPushButton#loginButton, QPushButton#logoutButton {{
            background-color: transparent;
            color: {COLORS['text_light']};
            border: 1px solid {COLORS['text_light']};
            text-align: left;
            padding: 10px;
        }}
        QPushButton#loginButton:hover, QPushButton#logoutButton:hover {{
            background-color: {COLORS['secondary']};
            color: white;
        }}
        /* --- Form Elements --- */
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {COLORS['background']};
            border: 1px solid #475569;
            padding: 8px;
            border-radius: 4px;
            font-size: 14px;
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {COLORS['accent']};
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox::down-arrow {{
            image: url(down_arrow.png); /* Cần có icon phù hợp */
        }}
        QLabel {{
            font-size: 14px;
        }}
        QFormLayout QLabel {{
             padding-top: 8px;
        }}
        /* --- Sidebar --- */
        QListWidget#sidebar {{
            border: none;
            font-size: 15px;
        }}
        QListWidget#sidebar::item {{
            padding: 12px 20px;
            border-radius: 6px;
        }}
        QListWidget#sidebar::item:selected, QListWidget#sidebar::item:hover {{
            background-color: {COLORS['secondary']};
            color: white;
        }}
        /* --- Tab Widget for Login View --- */
        QTabWidget::pane {{
            border: 1px solid {COLORS['secondary']};
            border-top: none;
            border-radius: 0 0 8px 8px;
        }}
        QTabBar::tab {{
            background: {COLORS['primary']};
            color: {COLORS['text_light']};
            padding: 12px 20px;
            font-size: 15px;
            font-weight: 600;
        }}
        QTabBar::tab:selected {{
            background: {COLORS['secondary']};
            color: white;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }}
        QTabBar::tab:!selected {{
            margin-top: 2px;
        }}
    """


# --- Hết phần giả lập ---


class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📄 Hệ thống Cấp số Văn bản (Offline)")
        self.resize(1280, 800)
        self.setStyleSheet(get_global_stylesheet())

        # --- THAY ĐỔI 1: Quản lý trạng thái và cấu trúc UI ---
        self.current_user_role = "Guest"  # Bắt đầu là Guest
        self.so_vanban_counter = 1
        self.vanban_log = []
        self.form_widgets = {}

        # Widget chính là một StackedWidget để chuyển đổi giữa các view
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)

        # Tạo các view chính
        self.login_view = self._create_login_view()
        self.main_app_view = self._create_main_app_view()

        # Thêm các view vào stack
        self.main_stack.addWidget(self.login_view)  # index 0
        self.main_stack.addWidget(self.main_app_view)  # index 1

        # Cập nhật giao diện ban đầu
        self._update_ui_for_role()

    # --- THAY ĐỔI 2: Tạo view đăng nhập riêng biệt ---
    def _create_login_view(self):
        """Tạo giao diện cho người dùng chưa đăng nhập."""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        # Frame chứa nội dung
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")
        layout = QVBoxLayout(login_frame)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # Tiêu đề
        title = QLabel("Hệ thống Cấp số Văn bản")
        title.setObjectName("h1")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Vui lòng chọn loại văn bản để lấy số, hoặc đăng nhập để truy cập các chức năng khác.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        # Tab widget cho hai form
        tab_widget = QTabWidget()

        # Tạo các trang cấp số và thêm vào tab
        fields_vb_mat = ["Nội dung", "Độ Mật", "Lãnh đạo duyệt ký", "Nơi nhận", "Đơn vị lưu", "Số lượng"]
        types_vb_mat = ["Báo cáo", "Công văn", "Kế hoạch", "Phương án", "Tờ trình", "Thông báo"]
        page_mat = self._create_doc_page("mat_login", "Văn bản Mật 🤫", types_vb_mat, fields_vb_mat, is_login_view=True)

        fields_vb_thuong = ["Nội dung", "Lãnh đạo duyệt ký", "Nơi nhận văn bản", "Đơn vị soạn thảo", "Số bản đóng dấu",
                            "Đơn vị lưu trữ"]
        types_vb_thuong = ["Báo cáo", "Công văn", "Kế hoạch", "Phiếu chuyển đơn", "Quyết định", "Thông báo", "Tờ trình"]
        page_thuong = self._create_doc_page("thuong_login", "Văn bản Thường 📄", types_vb_thuong, fields_vb_thuong,
                                            is_login_view=True)

        tab_widget.addTab(page_mat, "  Văn bản Mật  ")
        tab_widget.addTab(page_thuong, "  Văn bản Thường  ")

        # Nút đăng nhập
        login_btn = QPushButton("  Đăng nhập Admin")
        login_btn.setIcon(qta.icon("fa5s.sign-in-alt", color=COLORS['primary']))
        login_btn.clicked.connect(self._handle_login)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(tab_widget)
        layout.addWidget(login_btn, 0, Qt.AlignCenter)

        main_layout.addWidget(login_frame)
        return page

    # --- THAY ĐỔI 3: Tạo view chính của ứng dụng (sau khi đăng nhập) ---
    def _create_main_app_view(self):
        """Tạo giao diện chính với sidebar và các trang đầy đủ."""
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._create_sidebar(main_layout)
        self._create_main_content(main_layout)

        return main_widget

    def _create_sidebar(self, parent_layout):
        self.sidebar_container = QWidget()
        self.sidebar_container.setFixedWidth(240)
        self.sidebar_container.setStyleSheet(f"background-color: {COLORS['primary']};")

        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(5)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")

        sidebar_items = [
            ("fa5s.home", "Trang chủ"),
            ("fa5s.user-secret", "Văn bản Mật"),
            ("fa5s.file-alt", "Văn bản Thường"),
            ("fa5s.book", "Sổ quản lý Văn bản"),
            ("fa5s.users-cog", "Phân quyền"),
            ("fa5s.cogs", "Cài đặt"),
            ("fa5s.user", "Quản lý người dùng")
        ]
        for icon_name, text in sidebar_items:
            item = QListWidgetItem()
            icon = qta.icon(icon_name, color=COLORS['text_light'], color_active=COLORS['text'])
            item.setIcon(icon)
            item.setText(f"   {text}")
            item.setSizeHint(QSize(40, 40))
            self.sidebar.addItem(item)

        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()

        self.logout_btn = QPushButton("  Đăng xuất")
        self.logout_btn.setObjectName("logoutButton")
        self.logout_btn.setIcon(qta.icon("fa5s.sign-out-alt", color="white"))
        self.logout_btn.clicked.connect(self._handle_logout)
        sidebar_layout.addWidget(self.logout_btn, 0, Qt.AlignBottom)

        parent_layout.addWidget(self.sidebar_container)
        self.sidebar.currentRowChanged.connect(self.switch_page)

    # --- THAY ĐỔI 4: Hàm cập nhật UI đơn giản hơn, chỉ chuyển đổi view ---
    def _update_ui_for_role(self):
        """Chuyển đổi giữa view đăng nhập và view chính của ứng dụng."""
        if self.current_user_role == "Admin":
            self.main_stack.setCurrentIndex(1)  # Chuyển đến view chính
            self.sidebar.setCurrentRow(0)  # Mặc định chọn Trang chủ
            self.welcome_label.setText("Chào mừng Admin! 👋")
        else:  # Guest
            self.main_stack.setCurrentIndex(0)  # Chuyển về view đăng nhập

    def _handle_login(self):
        username, ok1 = QInputDialog.getText(self, "Đăng nhập", "Tên người dùng:")
        if not ok1 or not username.strip(): return

        password, ok2 = QInputDialog.getText(self, "Xác thực", "Nhập mật khẩu:", QLineEdit.Password)
        if not ok2 or not password.strip(): return

        hashed_password = hash_password(password.strip())
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = %s AND password_hash = %s",
                           (username.strip(), hashed_password))
            result = cursor.fetchone()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi cơ sở dữ liệu", str(e))
            return
        finally:
            if 'close' in dir(conn): conn.close()

        if result:
            self.current_user_role = result[0]
            self._update_ui_for_role()  # Cập nhật UI sau khi có vai trò mới
            QMessageBox.information(self, "Thành công", f"Đăng nhập thành công với vai trò: {self.current_user_role}")
        else:
            QMessageBox.warning(self, "Thất bại", "Tên đăng nhập hoặc mật khẩu không đúng.")

    def _handle_logout(self):
        self.current_user_role = "Guest"
        self._update_ui_for_role()
        QMessageBox.information(self, "Đăng xuất", "Bạn đã đăng xuất.")

    def _create_main_content(self, parent_layout):
        self.pages = QStackedWidget()
        parent_layout.addWidget(self.pages)

        fields_vb_mat = ["Nội dung", "Độ Mật", "Lãnh đạo duyệt ký", "Nơi nhận", "Đơn vị lưu", "Số lượng"]
        types_vb_mat = ["Báo cáo", "Công văn", "Kế hoạch", "Phương án", "Tờ trình", "Thông báo"]
        fields_vb_thuong = ["Nội dung", "Lãnh đạo duyệt ký", "Nơi nhận văn bản", "Đơn vị soạn thảo", "Số bản đóng dấu",
                            "Đơn vị lưu trữ"]
        types_vb_thuong = ["Báo cáo", "Công văn", "Kế hoạch", "Phiếu chuyển đơn", "Quyết định", "Thông báo", "Tờ trình"]

        self.pages.addWidget(self._create_home_page())
        self.pages.addWidget(self._create_doc_page("mat_main", "Văn bản Mật 🤫", types_vb_mat, fields_vb_mat))
        self.pages.addWidget(
            self._create_doc_page("thuong_main", "Văn bản Thường 📄", types_vb_thuong, fields_vb_thuong))

        log_page = QWidget()
        log_layout = QVBoxLayout(log_page)
        log_layout.setContentsMargins(30, 20, 30, 30)
        title = QLabel("Sổ quản lý Văn bản 📒")
        title.setObjectName("h2")
        log_layout.addWidget(title)
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Số VB", "Ngày", "Loại", "Trích yếu", "Trạng thái"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.log_table.setColumnWidth(3, 400)
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        log_layout.addWidget(self.log_table)
        self.pages.addWidget(log_page)

        self.pages.addWidget(self._create_placeholder_page("Phân quyền", "Admin có thể xem mọi thứ."))
        self.pages.addWidget(self._create_placeholder_page("Cài đặt", "Cấu hình tên đơn vị, đội,..."))
        self.pages.addWidget(create_user_management_page())

    def switch_page(self, index):
        if index >= 0 and self.sidebar.item(index).flags() & Qt.ItemIsEnabled:
            self.pages.setCurrentIndex(index)

    def _create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        self.welcome_label = QLabel()
        self.welcome_label.setObjectName("h1")
        layout.addWidget(self.welcome_label)

        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        self.total_docs_label = QLabel("0")
        self.canceled_docs_label = QLabel("0")
        stats_data = [
            {"icon": "fa5s.file-alt", "title": "Tổng văn bản đã cấp số", "value_widget": self.total_docs_label,
             "color": "#3B82F6"},
            {"icon": "fa5s.check-circle", "title": "Đã xác nhận", "value": "0", "color": "#10B981"},
            {"icon": "fa5s.clock", "title": "Chờ xác nhận", "value_widget": self.total_docs_label, "color": "#F59E0B"},
            {"icon": "fa5s.times-circle", "title": "Văn bản bị hủy", "value_widget": self.canceled_docs_label,
             "color": "#EF4444"},
        ]
        for i, data in enumerate(stats_data):
            value = data.get("value")
            value_widget = data.get("value_widget")
            card = self._create_stat_card(data['icon'], data['title'], value, value_widget, data['color'])
            stats_layout.addWidget(card, 0, i)
        layout.addLayout(stats_layout)
        layout.addStretch()
        return page

    def _create_stat_card(self, icon_name, title, value, value_widget, icon_bg_color):
        card = QFrame()
        card.setObjectName("statCard")
        layout = QHBoxLayout(card)
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon_name, color='white').pixmap(QSize(32, 32)))
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"background-color: {icon_bg_color}; border-radius: 30px;")
        text_layout = QVBoxLayout()
        title_label = QLabel(title)
        value_label = value_widget if value_widget else QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        return card

    def _create_doc_page(self, page_id, title_text, doc_types, form_fields, is_login_view=False):
        page = QWidget()
        layout = QVBoxLayout(page)
        # Bỏ lề và tiêu đề nếu là view đăng nhập để gọn hơn
        if is_login_view:
            layout.setContentsMargins(15, 20, 15, 20)
        else:
            layout.setContentsMargins(30, 20, 30, 30)
            title = QLabel(title_text)
            title.setObjectName("h2")
            layout.addWidget(title)

        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        form_card = QFrame()
        form_card.setObjectName("formCard" if not is_login_view else "")
        if is_login_view:
            form_card.setStyleSheet("background: transparent; border: none; padding: 0;")

        form_layout = QFormLayout(form_card)
        self.form_widgets[page_id] = {'inputs': []}

        result_label = QLabel("")
        result_label.setObjectName("resultLabel")
        result_label.setAlignment(Qt.AlignCenter)
        self.form_widgets[page_id]['result_label'] = result_label
        layout.addWidget(result_label)

        doc_type_combo = QComboBox()
        doc_type_combo.addItems(["-- Chọn loại văn bản --"] + doc_types)
        form_layout.addRow("Loại văn bản:", doc_type_combo)
        self.form_widgets[page_id]['inputs'].append(doc_type_combo)
        self.form_widgets[page_id]['doc_type'] = doc_type_combo

        for field_name in form_fields:
            if field_name == "Nội dung":
                widget = QTextEdit()
            elif field_name == "Độ Mật":
                widget = QComboBox()
                widget.addItems(["-- Chọn độ mật --", "MẬT", "TUYỆT MẬT", "TỐI MẬT"])
            else:
                widget = QLineEdit()
            widget.setPlaceholderText(f"Nhập {field_name.lower()}...")
            form_layout.addRow(f"{field_name}:", widget)
            self.form_widgets[page_id]['inputs'].append(widget)

        layout.addWidget(form_card)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        submit_btn = QPushButton("Lấy số văn bản")
        submit_btn.setObjectName("submitButton")
        submit_btn.setIcon(qta.icon("fa5s.check", color="white"))
        submit_btn.setEnabled(False)
        submit_btn.clicked.connect(partial(self._submit_document, page_id))
        btn_layout.addWidget(submit_btn)
        self.form_widgets[page_id]['button'] = submit_btn
        layout.addLayout(btn_layout)
        layout.addStretch()

        for widget in self.form_widgets[page_id]['inputs']:
            if isinstance(widget, (QLineEdit, QTextEdit)):
                widget.textChanged.connect(partial(self._validate_form, page_id))
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(partial(self._validate_form, page_id))
        return page

    def _validate_form(self, page_id):
        is_valid = all(
            (isinstance(w, QLineEdit) and w.text().strip() != "") or
            (isinstance(w, QTextEdit) and w.toPlainText().strip() != "") or
            (isinstance(w, QComboBox) and w.currentIndex() != 0)
            for w in self.form_widgets[page_id]['inputs']
        )
        self.form_widgets[page_id]['button'].setEnabled(is_valid)

    def _submit_document(self, page_id):
        doc_type_widget = self.form_widgets[page_id]['doc_type']
        doc_type_text = doc_type_widget.currentText()
        doc_type_code = "".join([c for c in doc_type_text if c.isupper()])
        ten_dv, doi = "TENDV", "DOI1"
        ngay_thang_nam = QDate.currentDate().toString("dd/MM/yyyy")
        so_van_ban = f"{self.so_vanban_counter:03d}/{doc_type_code}-{ten_dv}-{doi}"

        result_label = self.form_widgets[page_id]['result_label']
        result_label.setText(f"Số mới: {so_van_ban} ngày {ngay_thang_nam}")
        result_label.setStyleSheet(
            f"color: {COLORS['danger']}; font-size: 18px; font-weight: bold; padding: 10px; background-color: #33121b; border-radius: 6px;")
        self.so_vanban_counter += 1

        trich_yeu = next(
            (w.toPlainText().strip() for w in self.form_widgets[page_id]['inputs'] if isinstance(w, QTextEdit)), "")

        self.vanban_log.append({
            "so_vb": so_van_ban, "ngay": ngay_thang_nam, "loai": doc_type_text,
            "trich_yeu": trich_yeu, "trang_thai": "Chờ xác nhận"
        })
        self._update_log_table()
        self.total_docs_label.setText(str(len(self.vanban_log)))

        for widget in self.form_widgets[page_id]['inputs']:
            if isinstance(widget, (QLineEdit, QTextEdit)):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)

    def _update_log_table(self):
        if not hasattr(self, 'log_table'): return
        self.log_table.setRowCount(0)
        for row, entry in enumerate(reversed(self.vanban_log)):
            self.log_table.insertRow(row)
            items = [entry["so_vb"], entry["ngay"], entry["loai"], entry["trich_yeu"], entry["trang_thai"]]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                if col == 0 and entry["trang_thai"] == "Chờ xác nhận":
                    item.setForeground(QColor(COLORS['danger']))
                self.log_table.setItem(row, col, item)

    def _create_placeholder_page(self, title_text, message_text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        icon = QLabel()
        icon.setPixmap(qta.icon("fa5s.cogs", color="#94A3B8").pixmap(QSize(64, 64)))
        title = QLabel(f"Tính năng '{title_text}'")
        title.setObjectName("h2")
        message = QLabel(message_text + " 🛠️")
        for w in [icon, title, message]: w.setAlignment(Qt.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addStretch(2)
        return widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI")
    app.setFont(font)
    window = ModernApp()
    window.show()
    sys.exit(app.exec_())