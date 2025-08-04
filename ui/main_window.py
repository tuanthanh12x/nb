import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QListWidget, QListWidgetItem,
    QLineEdit, QFormLayout, QTextEdit, QComboBox, QFrame,
    QGridLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QDate, QSize, pyqtSignal
import qtawesome as qta
from functools import partial
import bcrypt

app = QApplication(sys.argv)
# Giả lập các module bị thiếu để code có thể chạy độc lập để demo
# Trong dự án thực tế, bạn sẽ dùng các file import thật
# --- START MOCK MODULES ---
class User:
    def __init__(self, username, password, full_name, role):
        self.username = username
        # Băm mật khẩu khi tạo user
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.full_name = full_name
        self.role = role  # 'admin' hoặc 'user'


class MockSession:
    def __init__(self):
        # Tạo sẵn một vài người dùng mẫu
        self.users = [
            User('admin', 'admin', 'Quản trị viên', 'admin'),
            User('thuyvy', '123', 'Nguyễn Thị Thúy Vy', 'user')
        ]

    def query(self, model):
        self._model = model
        return self

    def filter(self, condition):
        # Giả lập filter, chỉ hỗ trợ username == value
        attr_name = condition.left.name
        value = condition.right.value
        self._filtered_users = [u for u in self.users if getattr(u, attr_name) == value]
        return self

    def first(self):
        return self._filtered_users[0] if self._filtered_users else None

    def close(self):
        pass


def get_db_session():
    return MockSession()


def create_tables():
    print("Tạo bảng (giả lập)...")


COLORS = {
    "text_light": "#E2E8F0",
    "danger": "#EF4444",
}


def get_global_stylesheet():
    return """
        QWidget {
            font-family: Segoe UI;
            font-size: 14px;
            color: #CBD5E1;
        }
        QMainWindow {
            background-color: #0F172A;
        }
        /* Các style khác giữ nguyên như file styles.py của bạn */
        #sidebar {
            background-color: #1E293B;
            border-right: 1px solid #334155;
        }
        #sidebar::item {
            padding: 10px;
            border-radius: 5px;
        }
        #sidebar::item:selected {
            background-color: #3B82F6;
        }
        #h1 { font-size: 24px; font-weight: bold; }
        #h2 { font-size: 20px; font-weight: bold; }
        #submitButton {
            background-color: #3B82F6;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        #submitButton:disabled {
            background-color: #4B5563;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #334155;
            border: 1px solid #475569;
            padding: 8px;
            border-radius: 5px;
        }
        #statCard {
            background-color: #1E293B;
            border-radius: 8px;
        }
        #cardTitle { font-size: 13px; color: #94A3B8; }
        #cardValue { font-size: 22px; font-weight: bold; }
        #resultLabel { padding: 10px; }
    """


def create_log_page(parent):
    # Giả lập trang Sổ quản lý
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(30, 20, 30, 30)
    title = QLabel("Sổ quản lý Văn bản")
    title.setObjectName("h2")

    parent.log_table = QTableWidget()
    parent.log_table.setColumnCount(5)
    parent.log_table.setHorizontalHeaderLabels(["Số VB", "Ngày", "Loại", "Trích yếu", "Trạng thái"])
    parent.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    parent.log_table.setEditTriggers(QTableWidget.NoEditTriggers)

    layout.addWidget(title)
    layout.addWidget(parent.log_table)
    return page


def create_user_management_page(parent):
    # Giả lập trang Quản lý người dùng
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignCenter)
    label = QLabel("Đây là trang Quản lý người dùng.\nChỉ admin mới thấy trang này.")
    label.setObjectName("h2")
    layout.addWidget(label)
    return page


# --- END MOCK MODULES ---


class LoginWindow(QWidget):
    """
    Cửa sổ đăng nhập.
    Phát ra tín hiệu 'login_successful' khi đăng nhập thành công.
    """
    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.username = None  # Lưu trữ username nếu đăng nhập thành công
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Đăng nhập")
        self.setFixedSize(350, 220)
        self.setStyleSheet(get_global_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Hệ thống Cấp số Văn bản")
        title.setObjectName("h2")
        title.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tên đăng nhập")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mật khẩu")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Thêm giá trị mẫu để test nhanh
        self.username_input.setText("admin")
        self.password_input.setText("admin")

        form_layout.addRow("Tài khoản:", self.username_input)
        form_layout.addRow("Mật khẩu:", self.password_input)

        login_button = QPushButton("Đăng nhập")
        login_button.setObjectName("submitButton")
        login_button.clicked.connect(self._handle_login)
        self.password_input.returnPressed.connect(self._handle_login)

        layout.addWidget(title)
        layout.addSpacing(15)
        layout.addLayout(form_layout)
        layout.addSpacing(15)
        layout.addWidget(login_button)

    def _handle_login(self):
        username_text = self.username_input.text()
        password_text = self.password_input.text().encode('utf-8')

        db_session = get_db_session()
        try:
            user = db_session.query(User).filter(User.username == username_text).first()
            if user and bcrypt.checkpw(password_text, user.password_hash.encode('utf-8')):
                self.username = user.username  # Lưu lại username
                self.login_successful.emit(user.username)
                self.accept()  # Đóng dialog và trả về kết quả Accepted
            else:
                QMessageBox.warning(self, "Lỗi đăng nhập", "Tài khoản hoặc mật khẩu không chính xác!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi CSDL", f"Có lỗi xảy ra: {e}")
        finally:
            db_session.close()

    def exec_(self):
        """ Ghi đè exec_ để trả về username hoặc None. """
        super().exec_()
        return self.username


class ModernApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.current_user_username = username
        self._load_user_data()

        # Biến lưu trữ trạng thái ứng dụng
        self.so_vanban_counter = 1
        self.vanban_log = []
        self.form_widgets = {}

        self._setup_ui()
        self.sidebar.setCurrentRow(0)

    def _load_user_data(self):
        """Tải thông tin người dùng từ CSDL."""
        session = get_db_session()
        try:
            user_obj = session.query(User).filter(User.username == self.current_user_username).first()
            if user_obj:
                self.current_user_display_name = user_obj.full_name.split(' ')[
                    -1] if user_obj.full_name else self.current_user_username.capitalize()
                self.current_user_role = user_obj.role
            else:
                # Trường hợp dự phòng
                self.current_user_display_name = self.current_user_username.capitalize()
                self.current_user_role = 'user'  # An toàn là trên hết, mặc định là user
        finally:
            session.close()

    def _setup_ui(self):
        """Khởi tạo và sắp xếp toàn bộ giao diện người dùng."""
        self.setWindowTitle("📄 Hệ thống Cấp số Văn bản (Offline)")
        self.resize(1280, 800)
        self.setStyleSheet(get_global_stylesheet())

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        self._setup_navigation_and_pages(main_layout)

    def _setup_navigation_and_pages(self, parent_layout):
        """
        Tạo sidebar và các trang nội dung từ một cấu trúc định sẵn.
        Đây là cách tiếp cận "Single Source of Truth", giúp dễ quản lý.
        """
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setObjectName("sidebar")
        self.pages = QStackedWidget()

        parent_layout.addWidget(self.sidebar)
        parent_layout.addWidget(self.pages)

        # Định nghĩa tất cả các trang có thể có trong ứng dụng
        # 'factory' là một hàm sẽ tạo ra widget của trang đó
        # 'roles' là danh sách các vai trò có thể thấy trang này
        PAGES = [
            {"icon": "fa5s.home", "text": "Trang chủ", "factory": self._create_home_page, "roles": ["admin", "user"]},
            {"icon": "fa5s.user-secret", "text": "Văn bản Mật", "factory": self._create_vb_mat_page,
             "roles": ["admin", "user"]},
            {"icon": "fa5s.file-alt", "text": "Văn bản Thường", "factory": self._create_vb_thuong_page,
             "roles": ["admin", "user"]},
            {"icon": "fa5s.book", "text": "Sổ quản lý Văn bản", "factory": create_log_page, "roles": ["admin", "user"]},
            # Trang Quản lý người dùng chỉ dành cho admin
            {"icon": "fa5s.users-cog", "text": "Quản lý Người dùng", "factory": create_user_management_page,
             "roles": ["admin"]},
            {"icon": "fa5s.cogs", "text": "Cài đặt",
             "factory": lambda p: self._create_placeholder_page("Cài đặt", "Các cấu hình sẽ ở đây."),
             "roles": ["admin"]},
        ]

        for page_info in PAGES:
            # Chỉ thêm trang nếu vai trò của người dùng được phép
            if self.current_user_role in page_info["roles"]:
                # 1. Thêm mục vào Sidebar
                item = QListWidgetItem()
                icon = qta.icon(page_info["icon"], color=COLORS["text_light"], color_active=COLORS["text_light"])
                item.setIcon(icon)
                item.setText(f"   {page_info['text']}")
                item.setSizeHint(QSize(40, 40))
                self.sidebar.addItem(item)

                # 2. Tạo và thêm trang vào QStackedWidget
                page_widget = page_info["factory"](self)
                self.pages.addWidget(page_widget)

        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)

    def _create_home_page(self, parent):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel(f"Chào mừng trở lại, {self.current_user_display_name}! 👋")
        title.setObjectName("h1")
        layout.addWidget(title)

        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)

        self.total_docs_label = QLabel("0")
        self.canceled_docs_label = QLabel("0")

        stats_data = [
            {"icon": "fa5s.file-alt", "title": "Tổng văn bản", "value_widget": self.total_docs_label,
             "color": "#3B82F6"},
            {"icon": "fa5s.check-circle", "title": "Đã xác nhận", "value": "0", "color": "#10B981"},
            {"icon": "fa5s.clock", "title": "Chờ xác nhận", "value_widget": self.total_docs_label, "color": "#F59E0B"},
            {"icon": "fa5s.times-circle", "title": "Văn bản bị hủy", "value_widget": self.canceled_docs_label,
             "color": "#EF4444"},
        ]

        for i, data in enumerate(stats_data):
            card = self._create_stat_card(data['icon'], data['title'], data.get("value"), data.get("value_widget"),
                                          data['color'])
            stats_layout.addWidget(card, 0, i)

        layout.addLayout(stats_layout)
        layout.addStretch()
        return page

    # --- Tách các hàm tạo trang văn bản để dễ quản lý ---
    def _create_vb_mat_page(self, parent):
        fields = ["Nội dung", "Độ Mật", "Lãnh đạo duyệt ký", "Nơi nhận", "Đơn vị lưu", "Số lượng"]
        types = ["Báo cáo", "Công văn", "Kế hoạch", "Phương án", "Tờ trình", "Thông báo"]
        return self._create_doc_page("mat", "Văn bản Mật 🤫", types, fields)

    def _create_vb_thuong_page(self, parent):
        fields = ["Nội dung", "Lãnh đạo duyệt ký", "Nơi nhận văn bản", "Đơn vị soạn thảo", "Số bản đóng dấu",
                  "Đơn vị lưu trữ"]
        types = ["Báo cáo", "Công văn", "Kế hoạch", "Phiếu chuyển đơn", "Quyết định", "Thông báo", "Tờ trình"]
        return self._create_doc_page("thuong", "Văn bản Thường 📄", types, fields)

    # --- Các hàm helper (hỗ trợ) ---
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
        title_label.setObjectName("cardTitle")

        value_label = value_widget if value_widget else QLabel(value)
        value_label.setObjectName("cardValue")

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        return card

    def _create_doc_page(self, page_id, title_text, doc_types, form_fields):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel(title_text)
        title.setObjectName("h2")
        layout.addWidget(title)

        form_card = QFrame()
        form_card.setObjectName("formCard")
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
                widget.setPlaceholderText("Nhập trích yếu nội dung...")
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
            (isinstance(w, (QLineEdit, QTextEdit)) and w.text().strip() != "") or
            (isinstance(w, QComboBox) and w.currentIndex() != 0)
            for w in self.form_widgets[page_id]['inputs']
        )
        self.form_widgets[page_id]['button'].setEnabled(is_valid)

    def _submit_document(self, page_id):
        doc_type_text = self.form_widgets[page_id]['doc_type'].currentText()
        doc_type_code = "".join(c for c in doc_type_text if c.isupper())

        # TODO: Lấy các giá trị này từ CSDL hoặc file cấu hình
        ten_dv = "TENDV"
        doi = "DOI1"

        ngay_thang_nam = QDate.currentDate().toString("dd/MM/yyyy")
        so_hien_tai = self.so_vanban_counter
        so_van_ban = f"{so_hien_tai:03d}/{doc_type_code}-{ten_dv}-{doi}"

        self.so_vanban_counter += 1

        result_label = self.form_widgets[page_id]['result_label']
        result_label.setText(f"Số mới: {so_van_ban} ngày {ngay_thang_nam}")
        result_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 18px; font-weight: bold;")

        trich_yeu = next(
            (w.toPlainText().strip() for w in self.form_widgets[page_id]['inputs'] if isinstance(w, QTextEdit)), "")

        new_log_entry = {
            "so_vb": so_van_ban, "ngay": ngay_thang_nam, "loai": doc_type_text,
            "trich_yeu": trich_yeu, "trang_thai": "Chờ xác nhận"
        }
        self.vanban_log.append(new_log_entry)
        self._update_log_table()
        self.total_docs_label.setText(str(len(self.vanban_log)))

        for widget in self.form_widgets[page_id]['inputs']:
            if isinstance(widget, (QLineEdit, QTextEdit)):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)

    def _update_log_table(self):
        self.log_table.setRowCount(0)
        for row, entry in enumerate(reversed(self.vanban_log)):
            self.log_table.insertRow(row)
            so_vb_item = QTableWidgetItem(entry["so_vb"])
            if entry["trang_thai"] == "Chờ xác nhận":
                so_vb_item.setForeground(QColor(COLORS['danger']))
            self.log_table.setItem(row, 0, so_vb_item)
            self.log_table.setItem(row, 1, QTableWidgetItem(entry["ngay"]))
            self.log_table.setItem(row, 2, QTableWidgetItem(entry["loai"]))
            self.log_table.setItem(row, 3, QTableWidgetItem(entry["trich_yeu"]))
            self.log_table.setItem(row, 4, QTableWidgetItem(entry["trang_thai"]))

    def _create_placeholder_page(self, title_text, message_text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        icon = qta.icon("fa5s.cogs", color="#94A3B8")
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(QSize(64, 64)))
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(f"Tính năng '{title_text}'")
        title_label.setObjectName("h2")
        title_label.setAlignment(Qt.AlignCenter)

        message_label = QLabel(message_text + " 🛠️")
        message_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(message_label)
        return widget


if __name__ == "__main__":
    create_tables()  # Khởi tạo CSDL nếu cần
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI"))

    # Hiển thị cửa sổ đăng nhập và chờ người dùng tương tác
    login_dialog = LoginWindow()
    # .exec_() sẽ chặn luồng thực thi cho đến khi cửa sổ được đóng
    # và trả về username nếu đăng nhập thành công, hoặc None nếu thất bại/đóng ngang.
    username = login_dialog.exec_()

    # Chỉ khi nào đăng nhập thành công (username có giá trị) thì mới mở cửa sổ chính
    if username:
        main_window = ModernApp(username=username)
        main_window.show()
        sys.exit(app.exec_())
    else:
        # Nếu đăng nhập thất bại, ứng dụng sẽ thoát một cách êm ái
        sys.exit(0)