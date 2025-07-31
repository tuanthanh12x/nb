
# Bảng màu để dễ dàng quản lý
COLORS = {
    "primary": "#3B82F6",
    "primary_hover": "#2563EB",
    "primary_pressed": "#1D4ED8",
    "background": "#F1F5F9",
    "sidebar": "#1E293B",
    "text_light": "#F8FAFC",
    "text_dark": "#0F172A",
    "card": "#FFFFFF",
    "border": "#CBD5E1",
    "danger": "#EF4444",  # Màu đỏ cho số văn bản
}


def get_global_stylesheet():
    return f"""
        QMainWindow, QWidget {{
            background-color: {COLORS['background']};
        }}
        /* ---- Sidebar ---- */
        #sidebar {{
            background-color: {COLORS['sidebar']};
            border: none;
        }}
        #sidebar::item {{
            padding: 12px 20px; border-radius: 8px;
            color: {COLORS['text_light']}; font-size: 14px; font-weight: 500;
        }}
        #sidebar::item:hover {{ background-color: #334155; }}
        #sidebar::item:selected {{ background-color: {COLORS['primary']}; }}

        /* ---- Main Content ---- */
        QLabel#h1 {{ font-size: 24px; font-weight: 600; color: {COLORS['text_dark']}; }}
        QLabel#h2 {{ font-size: 20px; font-weight: 600; color: {COLORS['text_dark']}; }}
        QLabel#placeholder {{ font-size: 16px; color: #64748B; }}

        /* ---- Cards ---- */
        QFrame#statCard, QFrame#formCard {{
            background-color: {COLORS['card']};
            border-radius: 12px;
            border: 1px solid {COLORS['border']};
        }}
        QLabel#cardTitle {{ font-size: 14px; color: #475569; }}
        QLabel#cardValue {{ font-size: 28px; font-weight: 600; color: {COLORS['text_dark']}; }}

        /* ---- Form Widgets ---- */
        QLineEdit, QTextEdit, QComboBox, QDateEdit {{
            background-color: {COLORS['card']}; color: {COLORS['text_dark']};
            padding: 8px 12px; border: 1px solid {COLORS['border']};
            border-radius: 6px; font-size: 14px;
        }}
        QTextEdit {{ min-height: 80px; }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
            border: 2px solid {COLORS['primary']};
        }}
        QComboBox::drop-down {{ border: none; }}
        QFormLayout QLabel {{ font-size: 14px; font-weight: 500; padding-top: 8px; }}

        /* ---- Buttons ---- */
        QPushButton {{
            background-color: #E2E8F0; color: {COLORS['text_dark']};
            font-size: 14px; font-weight: 500;
            padding: 10px 20px; border-radius: 8px; border: none;
        }}
        QPushButton:hover {{ background-color: #CBD5E1; }}
        QPushButton#submitButton {{
            background-color: {COLORS['primary']}; color: {COLORS['text_light']};
            font-weight: 600; padding: 12px 24px;
        }}
        QPushButton#submitButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        QPushButton#submitButton:pressed {{ background-color: {COLORS['primary_pressed']}; }}
        QPushButton:disabled {{ background-color: #94A3B8; color: #E2E8F0; }}

        /* ---- Table ---- */
        QTableWidget {{
            background-color: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            gridline-color: {COLORS['border']};
        }}
        QHeaderView::section {{
            background-color: {COLORS['background']};
            padding: 8px;
            border: none;
            border-bottom: 1px solid {COLORS['border']};
            font-weight: 600;
        }}
    """
