# login_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
import bcrypt

# Giả định các file này nằm trong cùng thư mục hoặc trong Python path
from db.database import get_db_session, User
from ui.styles import get_global_stylesheet
