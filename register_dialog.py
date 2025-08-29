from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFormLayout, QComboBox, QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from modern_components import ModernLineEdit, ModernButton

class RegisterDialog(QDialog):
    def __init__(self, parent, firebase_manager):
        super().__init__(parent)
        self.firebase_manager = firebase_manager
        self.setWindowTitle("Registro de Empleado")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title = QLabel("Registro de Empleado")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.nombre_edit = ModernLineEdit("Nombre")
        self.apellido_edit = ModernLineEdit("Apellido")
        self.area_combo = QComboBox()
        self.area_combo.addItems(["Control de Calidad", "Distribucion", "Produccion", "Logistica","Administracion","Sistemas"])
        self.area_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #3498db;
            }
        """)
        self.puesto_combo = QComboBox()
        self.puesto_combo.addItems(["Operario", "Encargado", "Supervisor", "Administrativo","Administrador"])
        self.puesto_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #3498db;
            }

        """)

        # ComboBox para turno
        self.turno_combo = QComboBox()
        self.turno_combo.addItems(["Mañana", "Tarde", "Noche", "Rotativo"])
        self.turno_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #3498db;
            }
        """)
        
        # DateEdit para fecha de ingreso
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setStyleSheet("""
            QDateEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QDateEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Agregar campos al formulario
        form_layout.addRow("Nombre:", self.nombre_edit)
        form_layout.addRow("Apellido:", self.apellido_edit)
        form_layout.addRow("Área:", self.area_combo)
        form_layout.addRow("Puesto:", self.puesto_combo)
        form_layout.addRow("Fecha Ingreso:", self.fecha_edit)
        form_layout.addRow("Turno:", self.turno_combo)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.save_button = ModernButton("Guardar", "success")
        self.cancel_button = ModernButton("Cancelar", "secondary")
        
        self.save_button.clicked.connect(self.save_employee)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f4fd, stop:1 #f8fbff);
            }
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #34495e;
            }
        """)
    
    def generar_username(self, nombre, apellido):
        """Genera el username con primera letra del nombre + apellido"""
        if not nombre or not apellido:
            return ""
        return (nombre[0] + apellido).lower()
    
    def save_employee(self):
        # Validar campos
        if not all([
            self.nombre_edit.text().strip(),
            self.apellido_edit.text().strip(),
            self.area_combo.currentText().strip(),
            self.puesto_combo.currentText().strip()
        ]):
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
        
        # Generar username
        username = self.generar_username(
            self.nombre_edit.text().strip(),
            self.apellido_edit.text().strip()
        )
        
        # Generar EmpleadoID automático basado en timestamp y nombre
        import time
        timestamp = str(int(time.time()))[-6:]  # Últimos 6 dígitos del timestamp
        empleado_id = f"EMP{timestamp}{self.nombre_edit.text().strip()[:2].upper()}"
        
        # Crear datos del usuario
        datos_usuario = {
            'EmpleadoID': empleado_id,  # Generado automáticamente
            'Nombre': self.nombre_edit.text().strip(),
            'Apellido': self.apellido_edit.text().strip(),
            'Area': self.area_combo.currentText().strip(),
            'Puesto': self.puesto_combo.currentText().strip(),
            'FechaIngreso': self.fecha_edit.date().toString('yyyy-MM-dd'),
            'Turno': self.turno_combo.currentText(),
            'username': username,
            'fecha_registro': datetime.now().isoformat(),
            'password':'12345'
        }
        
        # Guardar en Firestore
        if self.firebase_manager.db and self.firebase_manager.registrar_usuario(datos_usuario):
            QMessageBox.information(self, "Éxito", 
                f"Empleado registrado exitosamente.\nEmpleadoID: {empleado_id}\nUsername: {username}")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Error al registrar el empleado")