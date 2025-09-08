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
from administrative_window import AdministrativeWindow
from operative_window import OperativeWindow
import requests
import json

# -----------------------------
# FACTORY PARA CREAR VENTANAS SEGÚN PUESTO
# -----------------------------
class WindowFactory:
    @staticmethod
    def create_window(usuario_data):
        puesto = usuario_data.get('Puesto', '').lower()
        is_temporal = usuario_data.get('temporal', False)
        
        # Si es temporal, usar la ventana temporal independientemente del puesto
        if is_temporal:
            from main_window import TemporalWindow
            return TemporalWindow(usuario_data)
        
        if puesto == 'administrativo':
            return AdministrativeWindow(usuario_data)
        elif puesto == 'operario':
            return OperativeWindow(usuario_data)
        else:
            # Para otros puestos, usar ventana genérica
            from main_window import MainWindow
            return MainWindow(usuario_data)

# -----------------------------
# CLASE PRINCIPAL PARA INTEGRACIÓN
# -----------------------------
class RoleBasedWindowManager:
    """Gestor principal para las ventanas basadas en roles"""
    
    def __init__(self):
        self.current_window = None
        self.usuario_data = None
    
    def create_window_for_user(self, usuario_data):
        """Crear ventana apropiada según el rol del usuario"""
        self.usuario_data = usuario_data
        
        # Usar el factory para crear la ventana adecuada
        self.current_window = WindowFactory.create_window(usuario_data)
        
        return self.current_window
    
    def get_current_window(self):
        """Obtener la ventana actual"""
        return self.current_window
    
    def close_current_window(self):
        """Cerrar la ventana actual"""
        if self.current_window:
            self.current_window.close()
            self.current_window = None

# -----------------------------
# FUNCIONES DE UTILIDAD
# -----------------------------
def format_datetime(timestamp_str):
    """Formatear timestamp para mostrar en la interfaz"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        return timestamp.strftime('%d/%m/%Y %H:%M:%S')
    except:
        return timestamp_str

def calculate_worked_hours(checkin_time, checkout_time):
    """Calcular horas trabajadas entre check-in y check-out"""
    try:
        if isinstance(checkin_time, str):
            checkin = datetime.fromisoformat(checkin_time)
        else:
            checkin = checkin_time
            
        if isinstance(checkout_time, str):
            checkout = datetime.fromisoformat(checkout_time)
        else:
            checkout = checkout_time
            
        worked_duration = checkout - checkin
        hours = worked_duration.total_seconds() / 3600
        return f"{int(hours)}:{int((hours % 1) * 60):02d}"
    except:
        return "0:00"

def validate_employee_data(employee_data):
    """Validar datos del empleado antes de enviar a la API"""
    required_fields = ['Nombre', 'Apellido', 'Area', 'Puesto', 'username']
    
    for field in required_fields:
        if not employee_data.get(field, '').strip():
            return False, f"El campo {field} es obligatorio"
    
    return True, "Datos válidos"

def get_status_color(status):
    """Obtener color según el estado"""
    status_colors = {
        'Activo': '#27ae60',
        'Inactivo': '#e74c3c', 
        'Temporal': '#f39c12',
        'Pendiente': '#f39c12',
        'Completado': '#27ae60',
        'Crítico': '#e74c3c',
        'Normal': '#27ae60',
        'Bajo': '#f39c12'
    }
    return status_colors.get(status, '#7f8c8d')

# -----------------------------
# CONFIGURACIÓN PARA INTEGRACIÓN CON MAIN_APP
# -----------------------------
def integrate_with_main_app():
    """
    Función para facilitar la integración con main_app.py
    Esta función debe ser llamada desde main_app.py para usar las ventanas por rol
    """
    def create_role_based_window(usuario_data):
        """Crear ventana basada en el rol del usuario"""
        return WindowFactory.create_window(usuario_data)
    
    return create_role_based_window

# Exportar función principal para main_app.py
create_role_based_window = integrate_with_main_app()