from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QStackedWidget, QFrame, QTextEdit, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from datetime import datetime, date, timedelta
from collections import defaultdict
from modern_components import ModernButton, ModernLineEdit
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import requests
import json

class WelcomePanel(QWidget):
    def __init__(self, usuario_data, role_specific_message="", parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.role_specific_message = role_specific_message
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_label = QLabel("¡Bienvenido al Sistema!")
        welcome_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        user_label = QLabel(f"{self.usuario_data.get('Nombre', '')} {self.usuario_data.get('Apellido', '')}")
        user_label.setStyleSheet("font-size: 24px; color: #34495e; margin-bottom: 15px;")
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        role_label = QLabel(f"Puesto: {self.usuario_data.get('Puesto', 'N/A')}")
        role_label.setStyleSheet("font-size: 18px; color: #7f8c8d; margin-bottom: 30px; font-weight: 600;")
        role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.role_specific_message:
            message_label = QLabel(self.role_specific_message)
            message_label.setStyleSheet("font-size: 16px; color: #3498db; font-style: italic; margin-bottom: 20px;")
            message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message_label.setWordWrap(True)
            layout.addWidget(message_label)

        info_label = QLabel("Selecciona una opción del panel lateral para comenzar")
        info_label.setStyleSheet("font-size: 16px; color: #7f8c8d; font-style: italic;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(welcome_label)
        layout.addWidget(user_label)
        layout.addWidget(role_label)
        layout.addWidget(info_label)

        self.setLayout(layout)
