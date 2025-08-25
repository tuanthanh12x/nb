# main.py
import sys
# Cần cài đặt thư viện: pip install PyQt5 qtawesome
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QListWidget, QListWidgetItem,
    QLineEdit, QMessageBox, QInputDialog, QGridLayout, QFrame, QDialog
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QSize
import qtawesome as qta

from core.user_manager import hash_password
from ui.user_manager_page import create_user_management_page
from ui.styles import COLORS, get_global_stylesheet
from db.db import get_conn
from ui.category_manager_page import create_category_management_page
# --- BƯỚC 1: IMPORT CÁC HÀM MỚI ---
from ui.document_manager_page import (
    create_document_creation_page,
    create_document_log_page,
    setup_document_management_logic,
    update_document_stats
)

class LoginDialog(QDialog):
    """
    Một cửa sổ dialog tùy chỉnh để đăng nhập, đẹp và tiện lợi hơn.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Đăng nhập Admin")
        self.setFixedSize(400, 280) # Kích thước cố định cho gọn gàng
        self.setStyleSheet(parent.styleSheet()) # Kế thừa style từ cửa sổ chính

        # Layout chính
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)

        # Tiêu đề
        title_label = QLabel("Đăng nhập")
        title_label.setObjectName("h2")
        title_label.setAlignment(Qt.AlignCenter)

        # Form điền thông tin
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(20)

        # Tên đăng nhập
        username_icon = QLabel()
        username_icon.setPixmap(qta.icon("fa5s.user", color=COLORS["text_secondary"]).pixmap(QSize(20, 20)))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên người dùng...")
        self.username_input.setFixedHeight(40)

        # Mật khẩu
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

        # Nút bấm
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.cancel_button = QPushButton("Hủy bỏ")
        self.cancel_button.setObjectName("cancelButton") # Đặt tên để có thể style riêng
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setObjectName("primaryButton") # Dùng style của nút chính
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)

        # Gắn các thành phần vào layout chính
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Kết nối tín hiệu
        self.login_button.clicked.connect(self.accept) # `accept` sẽ đóng dialog và trả về QDialog.Accepted
        self.cancel_button.clicked.connect(self.reject) # `reject` sẽ đóng dialog và trả về QDialog.Rejected

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

        # Các thuộc tính này sẽ được các hàm bên ngoài truy cập và thay đổi
        self.form_widgets = {}
        self.log_table = None
        self.log_search_input = None
        self.log_filter_type_combo = None
        self.log_filter_unit_combo = None
        self.log_filter_status_combo = None
        self.total_docs_label = None  # Sẽ được khởi tạo trong `_create_home_page`
        self.canceled_docs_label = None  # Sẽ được khởi tạo trong `_create_home_page`

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        self._create_sidebar(main_layout)
        self._create_main_content(main_layout)

        # Ánh xạ chỉ số sidebar tới chỉ số trang trong QStackedWidget
        self.page_indices_admin = {
            0: 1,  # Trang chủ
            1: 2,  # Văn bản Mật
            2: 3,  # Văn bản Thường
            3: 4,  # Sổ quản lý
            4: 5,  # Quản lý Danh mục
            5: 6,  # Phân quyền
            6: 7,  # Cài đặt
            7: 8  # Quản lý người dùng
        }
        self.page_indices_guest = {
            0: 0,  # Trang chủ Guest
            1: 2,  # Văn bản Mật
            2: 3  # Văn bản Thường
        }

        # --- BƯỚC 2: GỌI HÀM SETUP LOGIC TỪ FILE MỚI ---
        # Hàm này sẽ tải dữ liệu cho các combobox, và tải dữ liệu ban đầu cho sổ quản lý
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
                ("fa5s.users-cog", "Phân quyền"),
                ("fa5s.cogs", "Cài đặt"),
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

    def _create_guest_home_page(self) -> QWidget:
        """Tạo trang chủ dành cho người dùng Guest.

        Giao diện được thiết kế để thân thiện và rõ ràng (phiên bản không dùng icon file).
        """
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignCenter)  # Căn giữa toàn bộ nội dung

        # --- 1. Tiêu đề chính ---
        # Sử dụng ký tự emoji thay cho icon
        title = QLabel("Chào mừng bạn đến Hệ thống Cấp số Văn bản!")
        title.setObjectName("h1")
        title.setAlignment(Qt.AlignCenter)

        # --- 2. Lời giới thiệu ---
        intro = QLabel(
            "Bạn đang đăng nhập với quyền <b>Guest</b>. "
            "Các chức năng có thể sử dụng:"
        )
        intro.setWordWrap(True)
        intro.setAlignment(Qt.AlignCenter)
        intro.setObjectName("intro_text")

        # --- 3. Danh sách chức năng (trực quan hơn) ---
        features_frame = QFrame()
        features_frame.setObjectName("features_frame")
        features_layout = QVBoxLayout(features_frame)
        features_layout.setContentsMargins(20, 15, 20, 15)
        features_layout.setSpacing(15)

        # Sử dụng hàm trợ giúp để tránh lặp code
        features_layout.addWidget(self._create_feature_item("Lấy số văn bản Mật"))
        features_layout.addWidget(self._create_feature_item("Lấy số văn bản Thường"))

        # --- 4. Nút Kêu gọi Hành động (Call-to-Action) ---
        cta_label = QLabel("Nếu bạn là quản trị viên, hãy đăng nhập để có đầy đủ tính năng.")
        cta_label.setAlignment(Qt.AlignCenter)
        cta_label.setObjectName("placeholder")

        login_button = QPushButton("Đăng nhập Quản trị viên")
        login_button.setObjectName("cta_button")
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.clicked.connect(self._handle_login)
        # login_button.clicked.connect(self.show_login_dialog) # Kết nối tới hàm xử lý đăng nhập

        # --- Thêm các widget vào layout chính ---
        main_layout.addWidget(title)
        main_layout.addSpacing(10)
        main_layout.addWidget(intro)
        main_layout.addWidget(features_frame, 0, Qt.AlignCenter)
        main_layout.addStretch()  # Thêm khoảng trống co dãn
        main_layout.addWidget(cta_label)
        main_layout.addWidget(login_button, 0, Qt.AlignCenter)

        return page

    def _create_feature_item(self, text: str) -> QWidget:
        """Hàm trợ giúp tạo một dòng chức năng với ký tự check ✔️."""
        feature_widget = QWidget()
        layout = QHBoxLayout(feature_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Thay thế icon file bằng một QLabel chứa ký tự
        icon_label = QLabel("✔️")
        icon_label.setObjectName("feature_icon")  # Đặt tên để có thể style riêng nếu muốn

        text_label = QLabel(text)
        text_label.setObjectName("feature_label")

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()  # Đẩy nội dung về bên trái

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
        # Items sẽ được thêm trong _refresh_sidebar_items

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

        # Các mục menu chỉ admin thấy (dựa trên page_indices_admin)
        admin_only_indices = [3, 4, 5, 6, 7]

        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            if is_admin or i not in admin_only_indices:
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setForeground(QColor(COLORS['text_light']))
            else:
                item.setFlags(Qt.NoItemFlags)
                item.setForeground(QColor("#64748B"))

        self.login_btn.setVisible(not is_admin)
        self.logout_btn.setVisible(is_admin)

        # Cập nhật lời chào trên trang chủ admin nếu nó đã được tạo
        if hasattr(self, 'welcome_label'):
            welcome_text = "Chào mừng Admin! 👋" if is_admin else "Chào mừng bạn đến với Hệ thống"
            self.welcome_label.setText(welcome_text)

        # Cập nhật thống kê
        if is_admin:
            update_document_stats(self)

        # Chuyển về trang mặc định
        default_index = 0
        self.sidebar.setCurrentRow(default_index)
        self.switch_page(default_index)

    # --- BƯỚC 2: CẬP NHẬT LẠI HÀM _handle_login ---
    def _handle_login(self):
        # Tạo và hiển thị dialog đăng nhập tùy chỉnh
        login_dialog = LoginDialog(self)

        # .exec_() sẽ hiển thị dialog và chờ cho đến khi người dùng đóng nó
        # Nếu người dùng bấm "Đăng nhập" (nút đã connect với self.accept), nó sẽ trả về QDialog.Accepted
        if login_dialog.exec_() == QDialog.Accepted:
            username, password = login_dialog.get_credentials()

            if not username or not password:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                return

            hashed_password = hash_password(password)  # Mật khẩu không cần .strip() vì có thể có khoảng trắng
            try:
                conn = get_conn()
                cursor = conn.cursor()
                cursor.execute("SELECT role FROM users WHERE username = %s AND password_hash = %s",
                               (username, hashed_password))
                result = cursor.fetchone()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi cơ sở dữ liệu", str(e))
                return
            finally:
                if conn: conn.close()

            if result:
                self.current_user_role = result[0]
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

        # Index 0: Trang chủ Guest
        self.pages.addWidget(self._create_guest_home_page())
        # Index 1: Trang chủ Admin
        self.pages.addWidget(self._create_home_page())

        # --- BƯỚC 3: SỬ DỤNG HÀM TẠO TRANG TỪ FILE MỚI ---
        # Index 2: Trang tạo Văn bản Mật
        self.pages.addWidget(create_document_creation_page(self, "mat", "Văn bản Mật 🤫"))
        # Index 3: Trang tạo Văn bản Thường
        self.pages.addWidget(create_document_creation_page(self, "thuong", "Văn bản Thường 📄"))
        # Index 4: Trang Sổ quản lý văn bản
        self.pages.addWidget(create_document_log_page(self))

        # Các trang còn lại
        self.pages.addWidget(create_category_management_page())  # 5
        self.pages.addWidget(self._create_placeholder_page("Phân quyền", "Admin có thể xem mọi thứ..."))  # 6
        self.pages.addWidget(self._create_placeholder_page("Cài đặt", "Cấu hình tên đơn vị..."))  # 7
        self.pages.addWidget(create_user_management_page())  # 8

    def switch_page(self, index):
        if self.current_user_role == "Admin":
            mapping = self.page_indices_admin
        else:
            mapping = self.page_indices_guest

        page_index = mapping.get(index)
        item = self.sidebar.item(index)

        if item and (item.flags() & Qt.ItemIsEnabled) and page_index is not None:
            self.pages.setCurrentIndex(page_index)
            # Cập nhật thống kê khi chuyển sang trang chủ Admin
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

        # Khởi tạo các QLabel cho thống kê
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

        value_label = value_widget  # Sử dụng widget được truyền vào
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI")
    app.setFont(font)
    window = ModernApp()
    window.show()
    sys.exit(app.exec_())