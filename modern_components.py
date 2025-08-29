from PyQt6.QtWidgets import QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt

class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder_text=""):
        super().__init__()
        self.setPlaceholderText(placeholder_text)
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
            QLineEdit:hover {
                border: 2px solid rgba(52, 152, 219, 0.5);
            }
        """)

class ModernButton(QPushButton):
    def __init__(self, text, color="primary"):
        super().__init__(text)
        
        colors = {
            "primary": {
                "bg": "#3498db",
                "hover": "#2980b9",
                "pressed": "#21618c"
            },
            "success": {
                "bg": "#27ae60",
                "hover": "#229954",
                "pressed": "#1e8449"
            },
            "secondary": {
                "bg": "#95a5a6",
                "hover": "#7f8c8d",
                "pressed": "#6c7b7d"
            },
            "danger": {
                "bg": "#e74c3c",
                "hover": "#c0392b",
                "pressed": "#a93226"
            }
        }
        
        c = colors.get(color, colors["primary"])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c["bg"]}, stop:1 {c["hover"]});
                border: none;
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c["hover"]}, stop:1 {c["pressed"]});
            }}
            QPushButton:pressed {{
                background: {c["pressed"]};
            }}
            QPushButton:disabled {{
                background: #bdc3c7;
                color: #7f8c8d;
            }}
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class AnimatedCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(240, 248, 255, 0.95));
                border-radius: 20px;
                border: 1px solid rgba(52, 152, 219, 0.2);
            }
        """)
        self.setFixedSize(450, 550)