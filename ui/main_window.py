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

from db.database import get_db_session, User, create_tables
from ui.styles import get_global_stylesheet, COLORS
from ui.log_page import create_log_page
from .login import LoginWindow
import bcrypt
from ui.user_management import create_user_management_page

class ModernApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("📄 Hệ thống Cấp số Văn bản (Offline)")
        self.resize(1280, 800)
        self.setStyleSheet(get_global_stylesheet())

        session = get_db_session()
        try:
            user_obj = session.query(User).filter(User.username.ilike(username)).first()
            if user_obj:
                # Lấy tên để chào mừng (lấy tên cuối)
                self.current_user = user_obj.full_name.split(' ')[-1] if user_obj.full_name else username.capitalize()
                # Khởi tạo vai trò và username để dùng trong toàn bộ ứng dụng
                self.current_user_role = user_obj.role
                self.current_user_username = user_obj.username
            else:
                # Trường hợp dự phòng nếu không tìm thấy user
                self.current_user = username.capitalize()
                self.current_user_role = 'guest'  # Mặc định là guest
                self.current_user_username = username
        finally:
            session.close()  # Luôn đóng session sau khi dùng xong
        # --- KẾT THÚC PHẦN THÊM VÀO ---

        # Biến lưu trữ dữ liệu
        self.so_vanban_counter = 1  # Bộ đếm số văn bản
        self.vanban_log = []  # Nơi lưu trữ các văn bản đã cấp số
        self.form_widgets = {}  # Lưu các widget của form để kiểm tra và lấy dữ liệu

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        self._create_sidebar(main_layout)
        self._create_main_content(main_layout)

        self.sidebar.setCurrentRow(0)

    def _create_sidebar(self, parent_layout):
        """Tạo sidebar với các mục điều hướng theo yêu cầu."""
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setObjectName("sidebar")
        parent_layout.addWidget(self.sidebar)

        sidebar_items = [
            ("fa5s.home", "Trang chủ"),
            ("fa5s.user-secret", "Văn bản Mật"),
            ("fa5s.file-alt", "Văn bản Thường"),
            ("fa5s.book", "Sổ quản lý Văn bản"),
            ("fa5s.users-cog", "Phân quyền"),
            ("fa5s.users-cog", "Quản lý Người dùng"),
            ("fa5s.cogs", "Cài đặt")
        ]
        final_sidebar_items = []
        for icon, text in sidebar_items:
            if text == "Quản lý Người dùng" and self.current_user_role != 'admin':
                continue
            final_sidebar_items.append((icon, text))

        for icon_name, text in sidebar_items:
            item = QListWidgetItem()
            icon = qta.icon(icon_name, color=COLORS["text_light"], color_active=COLORS["text_light"])
            item.setIcon(icon)
            item.setText(f"   {text}")
            item.setSizeHint(QSize(40, 40))
            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(self.switch_page)

    def _create_main_content(self, parent_layout):
        """Tạo khu vực nội dung chính với các trang."""
        self.pages = QStackedWidget()
        parent_layout.addWidget(self.pages)

        # Định nghĩa các trường cho từng loại văn bản theo mô tả
        fields_vb_mat = ["Nội dung", "Độ Mật", "Lãnh đạo duyệt ký", "Nơi nhận", "Đơn vị lưu", "Số lượng"]
        types_vb_mat = ["Báo cáo", "Công văn", "Kế hoạch", "Phương án", "Tờ trình", "Thông báo"]

        fields_vb_thuong = ["Nội dung", "Lãnh đạo duyệt ký", "Nơi nhận văn bản", "Đơn vị soạn thảo", "Số bản đóng dấu",
                            "Đơn vị lưu trữ"]
        types_vb_thuong = ["Báo cáo", "Công văn", "Kế hoạch", "Phiếu chuyển đơn", "Quyết định", "Thông báo", "Tờ trình"]

        self.pages.addWidget(self._create_home_page())
        self.pages.addWidget(self._create_doc_page("mat", "Văn bản Mật 🤫", types_vb_mat, fields_vb_mat))
        self.pages.addWidget(self._create_doc_page("thuong", "Văn bản Thường 📄", types_vb_thuong, fields_vb_thuong))
        self.pages.addWidget(create_log_page(self))
        self.pages.addWidget(
            self._create_placeholder_page("Phân quyền", "Admin có thể xem mọi thứ. Khách chỉ có thể lấy số."))
        self.pages.addWidget(
            self._create_placeholder_page("Cài đặt", "Cấu hình tên đơn vị, đội,... sẽ được cập nhật ở đây."))

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)

    def _create_home_page(self):
        """Tạo trang chủ (dashboard) với các thẻ thống kê."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel(f"Chào mừng trở lại, {self.current_user}! 👋")
        title.setObjectName("h1")
        layout.addWidget(title)

        # Khu vực thẻ thống kê
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)

        self.total_docs_label = QLabel("0")  # Sẽ cập nhật sau
        self.canceled_docs_label = QLabel("0")  # Placeholder

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
        title_label.setObjectName("cardTitle")

        if value_widget:
            value_label = value_widget
        else:
            value_label = QLabel(value)

        value_label.setObjectName("cardValue")

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        return card

    def _create_doc_page(self, page_id, title_text, doc_types, form_fields):
        """Tạo trang nhập liệu văn bản động dựa trên tham số."""
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

        # Nơi hiển thị số văn bản mới
        self.form_widgets[page_id] = {'inputs': []}
        result_label = QLabel("")
        result_label.setObjectName("resultLabel")
        result_label.setAlignment(Qt.AlignCenter)
        self.form_widgets[page_id]['result_label'] = result_label
        layout.addWidget(result_label)

        # Tạo form
        doc_type_combo = QComboBox()
        doc_type_combo.addItems(["-- Chọn loại văn bản --"] + doc_types)
        form_layout.addRow("Loại văn bản:", doc_type_combo)
        self.form_widgets[page_id]['inputs'].append(doc_type_combo)
        self.form_widgets[page_id]['doc_type'] = doc_type_combo  # Lưu riêng để lấy tên loại VB

        for field_name in form_fields:
            label_text = f"{field_name}:"
            if field_name == "Nội dung":
                widget = QTextEdit()
                widget.setPlaceholderText("Nhập trích yếu nội dung...")
            elif field_name == "Độ Mật":
                widget = QComboBox()
                widget.addItems(["-- Chọn độ mật --", "MẬT", "TUYỆT MẬT", "TỐI MẬT"])
            else:
                widget = QLineEdit()
                widget.setPlaceholderText(f"Nhập {field_name.lower()}...")
            form_layout.addRow(label_text, widget)
            self.form_widgets[page_id]['inputs'].append(widget)

        layout.addWidget(form_card)

        # Nút hành động
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        submit_btn = QPushButton("Lấy số văn bản")
        submit_btn.setObjectName("submitButton")
        submit_btn.setIcon(qta.icon("fa5s.check", color="white"))
        submit_btn.setEnabled(False)  # Vô hiệu hóa ban đầu
        submit_btn.clicked.connect(partial(self._submit_document, page_id))
        btn_layout.addWidget(submit_btn)
        self.form_widgets[page_id]['button'] = submit_btn

        layout.addLayout(btn_layout)
        layout.addStretch()

        # Kết nối tín hiệu để kiểm tra form
        for widget in self.form_widgets[page_id]['inputs']:
            if isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
                widget.textChanged.connect(partial(self._validate_form, page_id))
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(partial(self._validate_form, page_id))

        return page

    def _validate_form(self, page_id):
        """Kiểm tra tất cả các trường, bật/tắt nút 'Lấy số'."""
        is_valid = True
        for widget in self.form_widgets[page_id]['inputs']:
            if isinstance(widget, QLineEdit) and widget.text().strip() == "":
                is_valid = False
                break
            if isinstance(widget, QTextEdit) and widget.toPlainText().strip() == "":
                is_valid = False
                break
            if isinstance(widget, QComboBox) and widget.currentIndex() == 0:
                is_valid = False
                break

        self.form_widgets[page_id]['button'].setEnabled(is_valid)

    def _submit_document(self, page_id):
        """Tạo số văn bản, hiển thị, lưu log và xóa form."""
        # 1. Tạo số văn bản
        doc_type_widget = self.form_widgets[page_id]['doc_type']
        doc_type_text = doc_type_widget.currentText()
        doc_type_code = "".join([c for c in doc_type_text if c.isupper()])  # VD: Công văn -> CV

        # Giả định tên đơn vị và đội
        ten_dv = "TENDV"
        doi = "DOI1"

        ngay_thang_nam = QDate.currentDate().toString("dd/MM/yyyy")
        so_hien_tai = self.so_vanban_counter

        # Format: xxx/BC-(tên ĐV)-Đội x
        so_van_ban = f"{so_hien_tai:03d}/{doc_type_code}-{ten_dv}-{doi}"
        full_so_van_ban_display = f"Số mới: {so_van_ban} ngày {ngay_thang_nam}"

        self.so_vanban_counter += 1

        # 2. Hiển thị số mới (màu đỏ)
        result_label = self.form_widgets[page_id]['result_label']
        result_label.setText(full_so_van_ban_display)
        result_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 18px; font-weight: bold; padding: 10px;")

        # 3. Lưu vào log
        trich_yeu = ""
        for i, widget in enumerate(self.form_widgets[page_id]['inputs']):
            # Tìm widget Nội dung/Trích yếu để lưu vào log
            if isinstance(widget, QTextEdit):
                trich_yeu = widget.toPlainText().strip()
                break

        new_log_entry = {
            "so_vb": so_van_ban,
            "ngay": ngay_thang_nam,
            "loai": doc_type_text,
            "trich_yeu": trich_yeu,
            "trang_thai": "Chờ xác nhận"
        }
        self.vanban_log.append(new_log_entry)
        self._update_log_table()
        self.total_docs_label.setText(str(len(self.vanban_log)))

        # 4. Xóa trắng form
        for widget in self.form_widgets[page_id]['inputs']:
            if isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)


    def _update_log_table(self):
        """Cập nhật lại dữ liệu trên bảng log."""
        self.log_table.setRowCount(0)  # Xóa dữ liệu cũ
        for row, entry in enumerate(reversed(self.vanban_log)):  # Hiển thị cái mới nhất lên đầu
            self.log_table.insertRow(row)

            so_vb_item = QTableWidgetItem(entry["so_vb"])
            # Theo yêu cầu, số mới cấp sẽ có màu đỏ
            if entry["trang_thai"] == "Chờ xác nhận":
                so_vb_item.setForeground(QColor(COLORS['danger']))

            self.log_table.setItem(row, 0, so_vb_item)
            self.log_table.setItem(row, 1, QTableWidgetItem(entry["ngay"]))
            self.log_table.setItem(row, 2, QTableWidgetItem(entry["loai"]))
            self.log_table.setItem(row, 3, QTableWidgetItem(entry["trich_yeu"]))
            self.log_table.setItem(row, 4, QTableWidgetItem(entry["trang_thai"]))

    def _create_placeholder_page(self, title_text, message_text):
        """Tạo một trang tạm thời cho các tính năng chưa phát triển."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        icon_label = QLabel()
        icon_label.setPixmap(qta.icon("fa5s.cogs", color="#94A3B8").pixmap(QSize(64, 64)))
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(f"Tính năng '{title_text}'")
        title_label.setObjectName("h2")
        title_label.setAlignment(Qt.AlignCenter)

        message_label = QLabel(message_text + " 🛠️")
        message_label.setObjectName("placeholder")
        message_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(message_label)
        return widget


if __name__ == "__main__":
    create_tables()
    app = QApplication(sys.argv)
    font = QFont("Segoe UI")
    app.setFont(font)

    # Biến để giữ tham chiếu đến cửa sổ chính, tránh bị xóa
    main_window = None

    def show_main_app(username):
        """Hàm để tạo và hiển thị cửa sổ chính sau khi đăng nhập."""
        global main_window
        main_window = ModernApp(username=username)
        main_window.show()

    # Tạo và hiển thị cửa sổ đăng nhập
    login_window = LoginWindow()
    # Kết nối tín hiệu đăng nhập thành công với hàm hiển thị cửa sổ chính
    login_window.login_successful.connect(show_main_app)
    login_window.show()

    sys.exit(app.exec_())