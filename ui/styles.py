
# Bảng màu để dễ dàng quản lý
COLORS = {
    "primary": "#0F172A",
    "primary_hover": "#2563EB",
    "primary_pressed": "#1D4ED8",
    "background": "#F1F5F9",
    "sidebar": "#1E293B",
    "text_light": "#F8FAFC",
    "text_dark": "#0F172A",
    "card": "#FFFFFF",
    "border": "#CBD5E1",
    "danger": "#EF4444",  # Màu đỏ cho số văn bản
    "accent": "#3B82F6",
"secondary": "#1E293B",
    "text_secondary":"#F8FAFC",
}


def get_global_stylesheet():
    return f"""
        QMainWindow {{
            background-color: {COLORS['background']};
        }}
        #sidebar {{
            background-color: {COLORS['primary']};
            border: none;
        }}
        #sidebar::item {{
            color: {COLORS['text_light']};
            padding: 10px;
            border-radius: 5px;
            margin: 5px 10px;
        }}
        #sidebar::item:selected, #sidebar::item:hover {{
            background-color: {COLORS['accent']};
        }}
        #h1 {{
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['text_dark']};
        }}
        #h2 {{
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_dark']};
        }}
        #placeholder, #cardTitle {{
            color: #64748B;
        }}
        #cardValue {{
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['text_dark']};
        }}
        #statCard, #formCard {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
        }}
        #resultLabel {{
            background-color: #E0F2FE; /* Light blue background for result */
            border: 1px solid {COLORS['accent']};
            border-radius: 5px;
            padding: 10px;
        }}
        QPushButton {{
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
        }}
        #submitButton, #loginButton {{
            background-color: {COLORS['accent']};
            color: white;
            border: none;
        }}
        #submitButton:hover, #loginButton:hover {{
            background-color: #2563EB;
        }}
        #submitButton:disabled {{
            background-color: #94A3B8;
        }}
        #logoutButton {{
             background-color: {COLORS['danger']};
             color: white;
             border: none;
        }}
        QLineEdit, QTextEdit, QComboBox {{
            padding: 8px;
            border: 1px solid #CBD5E1;
            border-radius: 5px;
            font-size: 14px;
        }}
        QHeaderView::section {{
            background-color: {COLORS['secondary']};
            color: {COLORS['text_light']};
            padding: 5px;
            border: 1px solid {COLORS['primary']};
            font-weight: bold;
        }}
        QTableWidget {{
            border: none;
            gridline-color: #E2E8F0;
        }}
    """

