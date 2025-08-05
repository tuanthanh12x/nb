# main.py
import sys
# Cần cài đặt thư viện: pip install PyQt5 qtawesome bcrypt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QListWidget, QListWidgetItem,
    QLineEdit, QMessageBox, QInputDialog, QGridLayout, QFrame, QDialog
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QSize
import qtawesome as qta

# --- SỬA ĐỔI IMPORT ---
# Import các hàm quản lý người dùng đã được sửa cho SQLite và bcrypt
from core.user_manager import validate_user
# Import các hàm quản lý CSDL
from db.db import initialize_database_if_needed
# Import các thành phần UI khác
from ui.user_manager_page import create_user_management_page
from ui.styles import COLORS, get_global_stylesheet
from ui.category_manager_page import create_category_management_page
from ui.document_manager_page import (
    create_document_creation_page,
    create_document_log_page,
    setup_document_management_logic,
    update_document_stats
)


class LoginDialog(QDialog):
    """
    Một cửa sổ dialog tùy chỉnh để đăng nhập, đẹp và tiện lợi hơn.
    (Không có thay đổi trong class này)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Đăng nhập")
        self.setFixedSize(400, 280)
        self.setStyleSheet(parent.styleSheet())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Đăng nhập")
        title_label.setObjectName("h2")
        title_label.setAlignment(Qt.AlignCenter)

        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(20)

        username_icon = QLabel()
        username_icon.setPixmap(qta.icon("fa5s.user", color=COLORS["text_secondary"]).pixmap(QSize(20, 20)))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên người dùng...")
        self.username_input.setFixedHeight(40)

        password_icon = QLabel()
        password_icon.setPixmap(qta.icon("fa5s.lock", color=COLORS["text_secondary"]).pixmap(QSize(20, 20)))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)

        form_layout.addWidget(username_icon, 0, 0)
        form_layout.addWidget(self.username_input, 0, 1)
        form_layout.addWidget(password_icon, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.cancel_button = QPushButton("Hủy bỏ")
        self.cancel_button.setObjectName("cancelButton")
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setObjectName("primaryButton")
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)

        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.login_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_credentials(self):
        """Trả về tên người dùng và mật khẩu đã nhập."""
        return self.username_input.text().strip(), self.password_input.text()


class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📄 Hệ thống Cấp số Văn bản (Offline)")
        self.resize(1280, 800)
        self.setStyleSheet(get_global_stylesheet())
        self.current_user_role = "Guest"

        self.form_widgets = {}
        self.log_table = None
        self.log_search_input = None
        self.log_filter_type_combo = None
        self.log_filter_unit_combo = None
        self.log_filter_status_combo = None
        self.total_docs_label = None
        self.confirmed_docs_label = None  # Thêm thuộc tính này
        self.pending_docs_label = None  # Thêm thuộc tính này
        self.canceled_docs_label = None

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        self._create_sidebar(main_layout)
        self._create_main_content(main_layout)

        # Ánh xạ chỉ số sidebar tới chỉ số trang trong QStackedWidget
        self.page_indices_admin = {
            0: 1,  # Trang chủ Admin
            1: 2,  # Văn bản Mật
            2: 3,  # Văn bản Thường
            3: 4,  # Sổ quản lý
            4: 5,  # Quản lý Danh mục
            5: 6   # Quản lý người dùng
        }
        self.page_indices_guest = {
            0: 0,  # Trang chủ Guest
            1: 2,  # Văn bản Mật
            2: 3  # Văn bản Thường
        }

        # Gọi hàm setup logic để tải dữ liệu cho các trang
        setup_document_management_logic(self)
        self._update_ui_for_role()

    def _refresh_sidebar_items(self):
        self.sidebar.clear()
        is_admin = (self.current_user_role == "Admin")
        if is_admin:
            sidebar_items = [
                ("fa5s.home", "Trang chủ"),
                ("fa5s.user-secret", "Văn bản Mật"),
                ("fa5s.file-alt", "Văn bản Thường"),
                ("fa5s.book", "Sổ quản lý Văn bản"),
                ("fa5s.database", "Quản lý Danh mục"),
                ("fa5s.user", "Quản lý người dùng")
            ]
        else:  # Guest
            sidebar_items = [
                ("fa5s.user", "Trang người dùng"),
                ("fa5s.user-secret", "Văn bản Mật"),
                ("fa5s.file-alt", "Văn bản Thường")
            ]
        for icon_name, text in sidebar_items:
            item = QListWidgetItem()
            icon = qta.icon(icon_name, color=COLORS["text_light"], color_active=COLORS["text_light"])
            item.setIcon(icon)
            item.setText(f"   {text}")
            item.setSizeHint(QSize(40, 40))
            self.sidebar.addItem(item)

    def _create_guest_home_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("🎉 Chào mừng bạn đến Hệ thống Cấp số Văn bản!")
        title.setObjectName("h1")
        title.setAlignment(Qt.AlignCenter)

        intro = QLabel("Bạn đang đăng nhập với quyền <b>Guest</b>. Các chức năng có thể sử dụng:")
        intro.setWordWrap(True)
        intro.setAlignment(Qt.AlignCenter)
        intro.setObjectName("intro_text")

        features_frame = QFrame()
        features_frame.setObjectName("features_frame")
        features_layout = QVBoxLayout(features_frame)
        features_layout.setContentsMargins(20, 15, 20, 15)
        features_layout.setSpacing(15)

        features_layout.addWidget(self._create_feature_item("Lấy số văn bản Mật"))
        features_layout.addWidget(self._create_feature_item("Lấy số văn bản Thường"))

        cta_label = QLabel("Nếu bạn là quản trị viên, hãy đăng nhập để có đầy đủ tính năng.")
        cta_label.setAlignment(Qt.AlignCenter)
        cta_label.setObjectName("placeholder")

        login_button = QPushButton("Đăng nhập Quản trị viên")
        login_button.setObjectName("cta_button")
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.clicked.connect(self._handle_login)

        main_layout.addWidget(title)
        main_layout.addSpacing(10)
        main_layout.addWidget(intro)
        main_layout.addWidget(features_frame, 0, Qt.AlignCenter)
        main_layout.addStretch()
        main_layout.addWidget(cta_label)
        main_layout.addWidget(login_button, 0, Qt.AlignCenter)
        return page

    def _create_feature_item(self, text: str):
        feature_widget = QWidget()
        layout = QHBoxLayout(feature_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        icon_label = QLabel("✔️")
        icon_label.setObjectName("feature_icon")
        text_label = QLabel(text)
        text_label.setObjectName("feature_label")
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        return feature_widget

    def _create_sidebar(self, parent_layout):
        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(240)
        sidebar_container.setStyleSheet(f"background-color: {COLORS['primary']};")
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 10, 0, 10)
        sidebar_layout.setSpacing(5)
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()
        self.login_btn = QPushButton("  Đăng nhập Admin")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setIcon(qta.icon("fa5s.sign-in-alt", color="white"))
        self.login_btn.clicked.connect(self._handle_login)
        sidebar_layout.addWidget(self.login_btn, 0, Qt.AlignBottom)
        self.logout_btn = QPushButton("  Đăng xuất")
        self.logout_btn.setObjectName("logoutButton")
        self.logout_btn.setIcon(qta.icon("fa5s.sign-out-alt", color="white"))
        self.logout_btn.clicked.connect(self._handle_logout)
        sidebar_layout.addWidget(self.logout_btn, 0, Qt.AlignBottom)
        parent_layout.addWidget(sidebar_container)
        self.sidebar.currentRowChanged.connect(self.switch_page)

    def _update_ui_for_role(self):
        is_admin = (self.current_user_role == "Admin")
        self._refresh_sidebar_items()
        self.login_btn.setVisible(not is_admin)
        self.logout_btn.setVisible(is_admin)
        if hasattr(self, 'welcome_label'):
            self.welcome_label.setText("Chào mừng Admin! 👋" if is_admin else "Chào mừng bạn đến với Hệ thống")
        if is_admin:
            update_document_stats(self)
        default_index = 0
        self.sidebar.setCurrentRow(default_index)
        self.switch_page(default_index)

    # --- SỬA ĐỔI QUAN TRỌNG: HÀM XỬ LÝ ĐĂNG NHẬP ---
    def _handle_login(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            username, password = login_dialog.get_credentials()
            if not username or not password:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                return

            # Sử dụng hàm validate_user đã được sửa đổi
            is_valid, role = validate_user(username, password)

            if is_valid:
                self.current_user_role = role
                self._update_ui_for_role()
                QMessageBox.information(self, "Thành công",
                                        f"Đăng nhập thành công với vai trò: {self.current_user_role}")
            else:
                QMessageBox.warning(self, "Thất bại", "Tên đăng nhập hoặc mật khẩu không đúng.")

    def _handle_logout(self):
        self.current_user_role = "Guest"
        self._update_ui_for_role()
        QMessageBox.information(self, "Đăng xuất", "Bạn đã đăng xuất.")

    def _create_main_content(self, parent_layout):
        self.pages = QStackedWidget()
        parent_layout.addWidget(self.pages)
        self.pages.addWidget(self._create_guest_home_page())  # 0
        self.pages.addWidget(self._create_home_page())  # 1
        self.pages.addWidget(create_document_creation_page(self, "mat", "Văn bản Mật 🤫"))  # 2
        self.pages.addWidget(create_document_creation_page(self, "thuong", "Văn bản Thường 📄"))  # 3
        self.pages.addWidget(create_document_log_page(self))  # 4
        self.pages.addWidget(create_category_management_page())  # 5
        self.pages.addWidget(create_user_management_page())  # 8

    def switch_page(self, index):
        mapping = self.page_indices_admin if self.current_user_role == "Admin" else self.page_indices_guest
        page_index = mapping.get(index)
        if page_index is not None:
            self.pages.setCurrentIndex(page_index)
            if self.current_user_role == "Admin" and page_index == 1:
                update_document_stats(self)

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
        self.confirmed_docs_label = QLabel("0")
        self.pending_docs_label = QLabel("0")
        self.canceled_docs_label = QLabel("0")
        stats_data = [
            {"icon": "fa5s.file-alt", "title": "Tổng văn bản đã cấp số", "widget": self.total_docs_label,
             "color": "#3B82F6"},
            {"icon": "fa5s.check-circle", "title": "Đã xác nhận", "widget": self.confirmed_docs_label,
             "color": "#10B981"},
            {"icon": "fa5s.clock", "title": "Chờ xác nhận", "widget": self.pending_docs_label, "color": "#F59E0B"},
            {"icon": "fa5s.times-circle", "title": "Văn bản bị hủy", "widget": self.canceled_docs_label,
             "color": "#EF4444"},
        ]
        for i, data in enumerate(stats_data):
            card = self._create_stat_card(data['icon'], data['title'], data['widget'], data['color'])
            stats_layout.addWidget(card, 0, i)
        layout.addLayout(stats_layout)
        layout.addStretch()
        return page

    def _create_stat_card(self, icon_name, title, value_widget, icon_bg_color):
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
        value_label = value_widget
        value_label.setObjectName("cardValue")
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        return card

    def _create_placeholder_page(self, title_text, message_text):
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


# --- SỬA ĐỔI QUAN TRỌNG: KHỐI CHẠY CHÍNH ---
if __name__ == "__main__":
    # 1. GỌI HÀM KHỞI TẠO CSDL NGAY KHI BẮT ĐẦU
    # Nó sẽ tự động kiểm tra và tạo CSDL cùng dữ liệu mẫu nếu cần.
    initialize_database_if_needed()

    # 2. Các đoạn code còn lại để chạy ứng dụng
    app = QApplication(sys.argv)
    font = QFont("Segoe UI")
    app.setFont(font)
    window = ModernApp()
    window.show()
    sys.exit(app.exec_())
