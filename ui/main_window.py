import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QStackedWidget,
    QListWidget, QLineEdit, QFormLayout
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt


class TailwindStyleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📄 Document Issuance System")
        self.resize(1100, 640)
        self.setStyleSheet(self.global_styles())

        # Main Layout
        layout = QHBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItems(["🏠 Home", "🔐 Secret Docs", "📄 Regular Docs", "⚙ Settings"])
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet(self.sidebar_styles())
        self.sidebar.currentRowChanged.connect(self.switch_page)
        layout.addWidget(self.sidebar)

        # Main content
        self.pages = QStackedWidget()
        layout.addWidget(self.pages)
        self.pages.addWidget(self.home_page())
        self.pages.addWidget(self.doc_page("Secret Document"))
        self.pages.addWidget(self.doc_page("Regular Document"))
        self.pages.addWidget(self.settings_page())

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)

    def home_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("📌 Welcome to the Document Issuance System")
        title.setFont(QFont("Segoe UI", 20))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        return widget

    def doc_page(self, title_text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel(f"✍️ {title_text}")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        form.setFormAlignment(Qt.AlignTop)
        form.setLabelAlignment(Qt.AlignLeft)
        form.addRow("🔤 Nội dung:", QLineEdit())
        form.addRow("🧑‍💼 Lãnh đạo duyệt ký:", QLineEdit())
        form.addRow("🏢 Nơi nhận:", QLineEdit())
        form.addRow("📁 Đơn vị lưu trữ:", QLineEdit())
        layout.addLayout(form)

        btn = QPushButton("📥 Lấy số văn bản")
        btn.setStyleSheet("padding: 10px 20px; background-color: #3B82F6; color: white; border-radius: 8px;")
        layout.addWidget(btn)
        layout.addStretch()
        return widget

    def settings_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("⚙ Settings")
        label.setFont(QFont("Segoe UI", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return widget

    def global_styles(self):
        return """
            QWidget {
                background-color: #F3F4F6;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #CBD5E0;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
                outline: none;
            }
        """

    def sidebar_styles(self):
        return """
            QListWidget {
                background-color: #1F2937;
                color: white;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 12px 10px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #3B82F6;
                color: white;
            }
        """


def run_app():
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#F3F4F6"))
    app.setPalette(palette)
    window = TailwindStyleApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
