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

# -----------------------------
# FACTORY PARA CREAR VENTANAS SEGÚN PUESTO
# -----------------------------
class WindowFactory:
    @staticmethod
    def create_window(usuario_data):
        puesto = usuario_data.get('Puesto', '').lower()
        
        if puesto == 'administrativo':
            return AdministrativeWindow(usuario_data)
        elif puesto == 'operario':
            return OperativeWindow(usuario_data)
        else:
            # Para otros puestos, usar ventana genérica (la original)
            from main_window import MainWindow
            return MainWindow(usuario_data)

# -----------------------------
# PANELES COMUNES
# -----------------------------
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

# -----------------------------
# VENTANA ADMINISTRATIVA
# -----------------------------
class AdministrativeWindow(QMainWindow):
    def __init__(self, usuario_data):
        super().__init__()
        self.usuario_data = usuario_data
        self.setWindowTitle("Sistema Administrativo - Gestión de Empleados")
        self.setFixedSize(1400, 900)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # ---------------- Sidebar Administrativo
        sidebar = QFrame()
        sidebar.setFixedWidth(320)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-right: 3px solid #3498db;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20,30,20,30)
        sidebar_layout.setSpacing(15)

        panel_title = QLabel("Panel Administrativo")
        panel_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                margin-bottom: 20px;
                padding: 15px;
                background-color: rgba(52, 152, 219, 0.3);
                border-radius: 10px;
            }
        """)
        sidebar_layout.addWidget(panel_title)

        # Botones específicos para administrativos
        self.btn_inicio = ModernButton("🏠 Inicio", "secondary")
        self.btn_empleados = ModernButton("👥 Gestionar Empleados", "primary")
        self.btn_reportes = ModernButton("📊 Reportes y Estadísticas", "success")
        self.btn_asistencia = ModernButton("⏰ Control de Asistencia", "warning")
        self.btn_config = ModernButton("⚙️ Configuración", "info")
        self.btn_salir = ModernButton("🚪 Salir", "danger")

        # Estilo especial para botones en sidebar oscuro
        button_style = """
            QPushButton {
                margin-bottom: 8px;
                font-size: 14px;
                font-weight: 600;
                text-align: left;
                padding: 15px 20px;
            }
        """
        for btn in [self.btn_inicio, self.btn_empleados, self.btn_reportes, 
                   self.btn_asistencia, self.btn_config, self.btn_salir]:
            btn.setStyleSheet(btn.styleSheet() + button_style)

        sidebar_layout.addWidget(self.btn_inicio)
        sidebar_layout.addWidget(self.btn_empleados)
        sidebar_layout.addWidget(self.btn_reportes)
        sidebar_layout.addWidget(self.btn_asistencia)
        sidebar_layout.addWidget(self.btn_config)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_salir)

        sidebar.setLayout(sidebar_layout)

        # ---------------- Área de contenido
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
            }
        """)
        
        # Crear paneles específicos para administrativos
        welcome_msg = "Tienes acceso completo al sistema para gestionar empleados, generar reportes y configurar el sistema."
        self.welcome_panel = WelcomePanel(self.usuario_data, welcome_msg)
        self.employee_management_panel = EmployeeManagementPanel()
        self.reports_panel = ReportsPanel()
        self.attendance_panel = AttendanceControlPanel()
        self.config_panel = ConfigurationPanel()

        self.content_area.addWidget(self.welcome_panel)           # 0
        self.content_area.addWidget(self.employee_management_panel) # 1
        self.content_area.addWidget(self.reports_panel)           # 2
        self.content_area.addWidget(self.attendance_panel)        # 3
        self.content_area.addWidget(self.config_panel)           # 4

        self.content_area.setCurrentIndex(0)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area, 1)
        central_widget.setLayout(main_layout)

        # Conexiones de botones
        self.btn_inicio.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        self.btn_empleados.clicked.connect(lambda: self.content_area.setCurrentIndex(1))
        self.btn_reportes.clicked.connect(lambda: self.content_area.setCurrentIndex(2))
        self.btn_asistencia.clicked.connect(lambda: self.content_area.setCurrentIndex(3))
        self.btn_config.clicked.connect(lambda: self.content_area.setCurrentIndex(4))
        self.btn_salir.clicked.connect(self.realizar_checkout)

    def realizar_checkout(self):
        """Checkout para administrativos"""
        checkout_data = {
            "EmpleadoID": self.usuario_data.get("EmpleadoID"),
            "username": self.usuario_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckOut"
        }
        
        try:
            response = requests.post('http://localhost:5000/register-evento', json=checkout_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Salida", "CheckOut registrado correctamente.")
                self.close()
            else:
                QMessageBox.warning(self, "Advertencia", "No se pudo registrar el checkout, pero puedes cerrar la aplicación.")
                self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar checkout: {str(e)}")

# -----------------------------
# VENTANA OPERATIVA
# -----------------------------
class OperativeWindow(QMainWindow):
    def __init__(self, usuario_data):
        super().__init__()
        self.usuario_data = usuario_data
        self.setWindowTitle("Sistema Operativo - Control de Producción")
        self.setFixedSize(1200, 800)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # ---------------- Sidebar Operativo
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #2ecc71);
                border-right: 3px solid #27ae60;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20,30,20,30)
        sidebar_layout.setSpacing(15)

        panel_title = QLabel("Panel Operativo")
        panel_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                margin-bottom: 20px;
                padding: 15px;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
            }
        """)
        sidebar_layout.addWidget(panel_title)

        # Botones específicos para operarios
        self.btn_inicio = ModernButton("🏠 Inicio", "secondary")
        self.btn_produccion = ModernButton("🏭 Control Producción", "success")
        self.btn_inventario = ModernButton("📦 Inventario", "primary")
        self.btn_reportar = ModernButton("📝 Reportar Incidencia", "warning")
        self.btn_mi_asistencia = ModernButton("⏰ Mi Asistencia", "info")
        self.btn_salir = ModernButton("🚪 Salir", "danger")

        # Estilo especial para sidebar verde
        button_style = """
            QPushButton {
                margin-bottom: 8px;
                font-size: 14px;
                font-weight: 600;
                text-align: left;
                padding: 15px 20px;
            }
        """
        for btn in [self.btn_inicio, self.btn_produccion, self.btn_inventario, 
                   self.btn_reportar, self.btn_mi_asistencia, self.btn_salir]:
            btn.setStyleSheet(btn.styleSheet() + button_style)

        sidebar_layout.addWidget(self.btn_inicio)
        sidebar_layout.addWidget(self.btn_produccion)
        sidebar_layout.addWidget(self.btn_inventario)
        sidebar_layout.addWidget(self.btn_reportar)
        sidebar_layout.addWidget(self.btn_mi_asistencia)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_salir)

        sidebar.setLayout(sidebar_layout)

        # ---------------- Área de contenido
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f5e8, stop:1 #c8e6c9);
            }
        """)
        
        # Crear paneles específicos para operarios
        welcome_msg = "Controla la producción, gestiona el inventario y reporta incidencias desde tu panel operativo."
        self.welcome_panel = WelcomePanel(self.usuario_data, welcome_msg)
        self.production_panel = ProductionControlPanel()
        self.inventory_panel = InventoryPanel()
        self.incident_panel = IncidentReportPanel(self.usuario_data)
        self.my_attendance_panel = MyAttendancePanel(self.usuario_data)

        self.content_area.addWidget(self.welcome_panel)        # 0
        self.content_area.addWidget(self.production_panel)     # 1
        self.content_area.addWidget(self.inventory_panel)      # 2
        self.content_area.addWidget(self.incident_panel)       # 3
        self.content_area.addWidget(self.my_attendance_panel)  # 4

        self.content_area.setCurrentIndex(0)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area, 1)
        central_widget.setLayout(main_layout)

        # Conexiones de botones
        self.btn_inicio.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        self.btn_produccion.clicked.connect(lambda: self.content_area.setCurrentIndex(1))
        self.btn_inventario.clicked.connect(lambda: self.content_area.setCurrentIndex(2))
        self.btn_reportar.clicked.connect(lambda: self.content_area.setCurrentIndex(3))
        self.btn_mi_asistencia.clicked.connect(lambda: self.content_area.setCurrentIndex(4))
        self.btn_salir.clicked.connect(self.realizar_checkout)

    def realizar_checkout(self):
        """Checkout para operarios"""
        checkout_data = {
            "EmpleadoID": self.usuario_data.get("EmpleadoID"),
            "username": self.usuario_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckOut"
        }
        
        try:
            response = requests.post('http://localhost:5000/register-evento', json=checkout_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Salida", "CheckOut registrado correctamente.")
                self.close()
            else:
                QMessageBox.warning(self, "Advertencia", "No se pudo registrar el checkout, pero puedes cerrar la aplicación.")
                self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar checkout: {str(e)}")

# -----------------------------
# DIALOGO PARA AGREGAR/EDITAR EMPLEADO
# -----------------------------
class EmployeeDialog(QDialog):
    def __init__(self, employee_data=None, parent=None):
        super().__init__(parent)
        self.employee_data = employee_data or {}
        self.is_edit_mode = employee_data is not None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Editar Empleado" if self.is_edit_mode else "Agregar Empleado")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        
        self.nombre_edit = QLineEdit(self.employee_data.get('Nombre', ''))
        self.apellido_edit = QLineEdit(self.employee_data.get('Apellido', ''))
        self.area_combo = QComboBox()
        self.area_combo.addItems(['Producción', 'Administración', 'Mantenimiento', 'Calidad', 'Logística'])
        self.area_combo.setCurrentText(self.employee_data.get('Area', ''))
        
        self.puesto_combo = QComboBox()
        self.puesto_combo.addItems(['Operario', 'Administrativo', 'Supervisor', 'Técnico', 'Analista'])
        self.puesto_combo.setCurrentText(self.employee_data.get('Puesto', ''))
        
        self.turno_combo = QComboBox()
        self.turno_combo.addItems(['Mañana', 'Tarde', 'Noche', 'Rotativo'])
        self.turno_combo.setCurrentText(self.employee_data.get('Turno', ''))
        
        self.username_edit = QLineEdit(self.employee_data.get('username', ''))
        
        form_layout.addRow("Nombre:", self.nombre_edit)
        form_layout.addRow("Apellido:", self.apellido_edit)
        form_layout.addRow("Área:", self.area_combo)
        form_layout.addRow("Puesto:", self.puesto_combo)
        form_layout.addRow("Turno:", self.turno_combo)
        form_layout.addRow("Username:", self.username_edit)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)

    def get_employee_data(self):
        return {
            'Nombre': self.nombre_edit.text(),
            'Apellido': self.apellido_edit.text(),
            'Area': self.area_combo.currentText(),
            'Puesto': self.puesto_combo.currentText(),
            'Turno': self.turno_combo.currentText(),
            'username': self.username_edit.text(),
            'FechaIngreso': date.today().isoformat() if not self.is_edit_mode else self.employee_data.get('FechaIngreso', date.today().isoformat())
        }

# -----------------------------
# PANELES ESPECÍFICOS PARA ADMINISTRATIVOS
# -----------------------------
class EmployeeManagementPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Gestión de Empleados")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Botones de acción
        action_layout = QHBoxLayout()
        self.btn_add_employee = ModernButton("➕ Agregar Empleado", "success")
        self.btn_edit_employee = ModernButton("✏️ Editar Empleado", "primary")
        self.btn_delete_employee = ModernButton("🗑️ Eliminar Empleado", "danger")
        self.btn_refresh = ModernButton("🔄 Actualizar", "secondary")
        
        action_layout.addWidget(self.btn_add_employee)
        action_layout.addWidget(self.btn_edit_employee)
        action_layout.addWidget(self.btn_delete_employee)
        action_layout.addWidget(self.btn_refresh)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)

        # Tabla de empleados
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID Empleado", "Nombre", "Apellido", "Área", "Puesto", 
            "Turno", "Fecha Ingreso", "Username", "Estado"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Estilo para la tabla
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        """)
        
        layout.addWidget(self.table)

        # Conectar botones
        self.btn_refresh.clicked.connect(self.load_employees)
        self.btn_add_employee.clicked.connect(self.add_employee)
        self.btn_edit_employee.clicked.connect(self.edit_employee)
        self.btn_delete_employee.clicked.connect(self.delete_employee)
        
        self.setLayout(layout)

    def load_employees(self):
        try:
            response = requests.get('http://localhost:5000/get-empleados')
            if response.status_code == 200:
                empleados = response.json()

                self.table.setRowCount(len(empleados))
                for row, emp in enumerate(empleados):
                    items = [
                        emp.get("EmpleadoID", "N/A"),
                        emp.get("Nombre", "N/A"),
                        emp.get("Apellido", "N/A"),
                        emp.get("Area", "N/A"),
                        emp.get("Puesto", "N/A"),
                        emp.get("Turno", "N/A"),
                        emp.get("FechaIngreso", "N/A"),
                        emp.get("username", "N/A"),
                        "Temporal" if emp.get("temporal", False) else "Activo"
                    ]
                    for col, text in enumerate(items):
                        item = QTableWidgetItem(str(text))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        # Color diferente para empleados temporales
                        if items[8] == "Temporal":
                            item.setBackground(Qt.GlobalColor.yellow)
                        self.table.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando empleados: {str(e)}")

    def add_employee(self):
        dialog = EmployeeDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            employee_data = dialog.get_employee_data()
            employee_data['temporal'] = True  # Marcar como temporal
            employee_data['EmpleadoID'] = f"TEMP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            try:
                response = requests.post('http://localhost:5000/add-empleado', json=employee_data)
                if response.status_code == 200:
                    QMessageBox.information(self, "Éxito", "Empleado agregado como temporal correctamente.")
                    self.load_employees()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo agregar el empleado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error agregando empleado: {str(e)}")

    def edit_employee(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selección", "Por favor selecciona un empleado para editar.")
            return
        
        # Obtener datos del empleado seleccionado
        employee_data = {}
        headers = ["EmpleadoID", "Nombre", "Apellido", "Area", "Puesto", "Turno", "FechaIngreso", "username"]
        for col, header in enumerate(headers):
            item = self.table.item(current_row, col)
            if item:
                employee_data[header] = item.text()
        
        dialog = EmployeeDialog(employee_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_employee_data()
            updated_data['EmpleadoID'] = employee_data['EmpleadoID']  # Mantener el ID original
            
            try:
                response = requests.put(f'http://localhost:5000/update-empleado/{employee_data["EmpleadoID"]}', json=updated_data)
                if response.status_code == 200:
                    QMessageBox.information(self, "Éxito", "Empleado actualizado correctamente.")
                    self.load_employees()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo actualizar el empleado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error actualizando empleado: {str(e)}")

    def delete_employee(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selección", "Por favor selecciona un empleado para eliminar.")
            return
        
        empleado_id_item = self.table.item(current_row, 0)
        if not empleado_id_item:
            QMessageBox.warning(self, "Error", "No se puede obtener el ID del empleado.")
            return
        
        empleado_id = empleado_id_item.text()
        nombre_item = self.table.item(current_row, 1)
        apellido_item = self.table.item(current_row, 2)
        nombre_completo = f"{nombre_item.text() if nombre_item else ''} {apellido_item.text() if apellido_item else ''}"
        
        reply = QMessageBox.question(
            self, 
            "Confirmar Eliminación", 
            f"¿Estás seguro de que quieres eliminar al empleado {nombre_completo}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.delete(f'http://localhost:5000/delete-empleado/{empleado_id}')
                if response.status_code == 200:
                    QMessageBox.information(self, "Éxito", "Empleado eliminado correctamente.")
                    self.load_employees()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el empleado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error eliminando empleado: {str(e)}")

class ReportsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_reports()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Reportes y Estadísticas")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Botón para actualizar datos
        button_layout = QHBoxLayout()
        self.btn_refresh = ModernButton("🔄 Actualizar Reportes", "primary")
        self.btn_refresh.clicked.connect(self.load_reports)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Área de gráficos con scroll si es necesario
        self.figure = Figure(figsize=(16, 12))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def load_reports(self):
        try:
            self.figure.clear()
            
            # Crear los 4 gráficos específicos solicitados
            ax1 = self.figure.add_subplot(2, 2, 1)  # Cantidad producida 2024
            ax2 = self.figure.add_subplot(2, 2, 2)  # Desperdicio y producción por trimestre
            ax3 = self.figure.add_subplot(2, 2, 3)  # Suma de ingresos y egresos por sector
            ax4 = self.figure.add_subplot(2, 2, 4)  # Cumplimiento de turnos por área
            
            self.create_production_2024_chart(ax1)
            self.create_quarterly_waste_production_chart(ax2)
            self.create_income_expenses_by_sector_chart(ax3)
            self.create_shift_compliance_by_area_chart(ax4)
            
            self.figure.tight_layout(pad=3.0)
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error generando reportes: {e}")

    def create_production_2024_chart(self, ax):
        """Gráfico de cantidad producida en 2024"""
        try:
            # Obtener datos de producción del 2024
            produccion_data = self.get_produccion_data()
            
            # Filtrar datos del 2024 y agrupar por mes
            monthly_production = defaultdict(int)
            
            for prod in produccion_data:
                try:
                    timestamp_str = prod.get('timestamp', '')
                    if timestamp_str.startswith('2024'):
                        timestamp = datetime.fromisoformat(timestamp_str)
                        month_key = timestamp.strftime('%Y-%m')
                        cantidad = prod.get('cantidad', 0)
                        monthly_production[month_key] += cantidad
                except:
                    continue
            
            # Si no hay datos reales, usar datos de ejemplo
            if not monthly_production:
                monthly_production = {
                    '2024-01': 1200, '2024-02': 1450, '2024-03': 1680, '2024-04': 1320,
                    '2024-05': 1590, '2024-06': 1750, '2024-07': 1890, '2024-08': 1650,
                    '2024-09': 1420, '2024-10': 1580, '2024-11': 1720, '2024-12': 1900
                }
            
            # Preparar datos para el gráfico
            months = sorted(monthly_production.keys())
            production_values = [monthly_production[month] for month in months]
            month_labels = [datetime.strptime(month, '%Y-%m').strftime('%b') for month in months]
            
            # Crear gráfico de barras con gradiente
            bars = ax.bar(month_labels, production_values, color='#3498db', alpha=0.8, edgecolor='#2980b9', linewidth=2)
            
            # Agregar valores en las barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(production_values)*0.01,
                       f'{int(height):,}', ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            ax.set_title('Cantidad Producida 2024', fontweight='bold', fontsize=14, pad=15)
            ax.set_xlabel('Mes', fontweight='bold')
            ax.set_ylabel('Unidades Producidas', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_ylim(0, max(production_values) * 1.1)
            
            # Mejorar formato de números en el eje Y
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error cargando datos de producción\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)

    def create_quarterly_waste_production_chart(self, ax):
        """Gráfico de desperdicio y producción por trimestre"""
        try:
            # Obtener datos de producción y desperdicios
            produccion_data = self.get_produccion_data()
            desperdicio_data = self.get_desperdicio_data()
            
            # Agrupar por trimestre
            quarterly_production = defaultdict(int)
            quarterly_waste = defaultdict(int)
            
            # Procesar datos de producción
            for prod in produccion_data:
                try:
                    timestamp_str = prod.get('timestamp', '')
                    if timestamp_str.startswith('2024'):
                        timestamp = datetime.fromisoformat(timestamp_str)
                        quarter = f"Q{(timestamp.month - 1) // 3 + 1} 2024"
                        quarterly_production[quarter] += prod.get('cantidad', 0)
                except:
                    continue
            
            # Procesar datos de desperdicio
            for waste in desperdicio_data:
                try:
                    timestamp_str = waste.get('timestamp', '')
                    if timestamp_str.startswith('2024'):
                        timestamp = datetime.fromisoformat(timestamp_str)
                        quarter = f"Q{(timestamp.month - 1) // 3 + 1} 2024"
                        quarterly_waste[quarter] += waste.get('cantidad', 0)
                except:
                    continue
            
            # Si no hay datos reales, usar datos de ejemplo
            if not quarterly_production:
                quarterly_production = {'Q1 2024': 4330, 'Q2 2024': 4660, 'Q3 2024': 4960, 'Q4 2024': 5200}
                quarterly_waste = {'Q1 2024': 215, 'Q2 2024': 280, 'Q3 2024': 248, 'Q4 2024': 312}
            
            quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
            production_values = [quarterly_production.get(q, 0) for q in quarters]
            waste_values = [quarterly_waste.get(q, 0) for q in quarters]
            
            # Crear gráfico de barras agrupadas
            x = range(len(quarters))
            width = 0.35
            
            bars1 = ax.bar([i - width/2 for i in x], production_values, width, 
                          label='Producción', color='#27ae60', alpha=0.8)
            bars2 = ax.bar([i + width/2 for i in x], waste_values, width,
                          label='Desperdicio', color='#e74c3c', alpha=0.8)
            
            # Agregar valores en las barras
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + max(max(production_values), max(waste_values))*0.01,
                           f'{int(height):,}', ha='center', va='bottom', fontweight='bold', fontsize=8)
            
            ax.set_title('Desperdicio y Producción por Trimestre', fontweight='bold', fontsize=14, pad=15)
            ax.set_xlabel('Trimestre', fontweight='bold')
            ax.set_ylabel('Unidades', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(quarters)
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Formato de números
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error cargando datos de desperdicio\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)

    def create_income_expenses_by_sector_chart(self, ax):
        """Gráfico de suma de check-ins y check-outs por área"""
        try:
            # Obtener datos de empleados y eventos
            empleados_data = self.get_empleados_data()
            eventos_data = self.get_eventos_data()
            
            # Crear mapeo de empleado ID a área
            empleado_to_area = {}
            for emp in empleados_data:
                empleado_to_area[emp.get('EmpleadoID')] = emp.get('Area', 'Sin Área')
            
            # Agrupar eventos por área
            area_checkins = defaultdict(int)
            area_checkouts = defaultdict(int)
            
            # Filtrar eventos del día actual o período deseado
            today = date.today().isoformat()
            
            for evento in eventos_data:
                empleado_id = evento.get('EmpleadoID')
                timestamp = evento.get('timestamp', '')
                evento_tipo = evento.get('evento')
                
                # Filtrar por fecha si es necesario (aquí filtro por hoy)
                if timestamp.startswith(today) and empleado_id in empleado_to_area:
                    area = empleado_to_area[empleado_id]
                    
                    if evento_tipo == 'CheckIn':
                        area_checkins[area] += 1
                    elif evento_tipo == 'CheckOut':
                        area_checkouts[area] += 1
            
            # Si no hay datos reales, usar datos de ejemplo
            if not area_checkins and not area_checkouts:
                area_checkins = {
                    'Producción': 18, 'Administración': 8, 
                    'Mantenimiento': 5, 'Calidad': 6, 'Logística': 9
                }
                area_checkouts = {
                    'Producción': 15, 'Administración': 7,
                    'Mantenimiento': 4, 'Calidad': 6, 'Logística': 8
                }
            
            # Obtener todas las áreas únicas
            all_areas = set(list(area_checkins.keys()) + list(area_checkouts.keys()))
            areas = sorted(list(all_areas))
            
            checkin_values = [area_checkins.get(area, 0) for area in areas]
            checkout_values = [area_checkouts.get(area, 0) for area in areas]
            
            # Crear gráfico de barras agrupadas
            x = range(len(areas))
            width = 0.35
            
            bars1 = ax.bar([i - width/2 for i in x], checkin_values, width,
                        label='Check-In', color='#27ae60', alpha=0.8)
            bars2 = ax.bar([i + width/2 for i in x], checkout_values, width,
                        label='Check-Out', color='#e74c3c', alpha=0.8)
            
            # Agregar valores en las barras
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + max(max(checkin_values), max(checkout_values))*0.01,
                            f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            ax.set_title('Suma de Check-In y Check-Out por Área', fontweight='bold', fontsize=14, pad=15)
            ax.set_xlabel('Área', fontweight='bold')
            ax.set_ylabel('Cantidad de Eventos', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(areas, rotation=45, ha='right')
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Establecer límites del eje Y
            max_val = max(max(checkin_values) if checkin_values else [0], 
                        max(checkout_values) if checkout_values else [0])
            ax.set_ylim(0, max_val * 1.1 if max_val > 0 else 10)
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error cargando datos de eventos\n{str(e)}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=10)

    def create_shift_compliance_by_area_chart(self, ax):
        """Gráfico de cumplimiento de turnos por área"""
        try:
            # Obtener datos de asistencia y empleados
            empleados_data = self.get_empleados_data()
            eventos_data = self.get_eventos_data()
            
            # Analizar cumplimiento por área
            area_compliance = defaultdict(lambda: {'SI': 0, 'NO': 0})
            
            # Obtener empleados por área
            empleados_por_area = defaultdict(list)
            for emp in empleados_data:
                area = emp.get('Area', 'Sin Área')
                empleados_por_area[area].append(emp.get('EmpleadoID'))
            
            # Analizar asistencia del día actual
            today = date.today().isoformat()
            empleados_con_checkin = set()
            
            for evento in eventos_data:
                if (evento.get('timestamp', '').startswith(today) and 
                    evento.get('evento') == 'CheckIn'):
                    empleados_con_checkin.add(evento.get('EmpleadoID'))
            
            # Calcular cumplimiento por área
            for area, empleados_ids in empleados_por_area.items():
                for emp_id in empleados_ids:
                    if emp_id in empleados_con_checkin:
                        area_compliance[area]['SI'] += 1
                    else:
                        area_compliance[area]['NO'] += 1
            
            # Si no hay datos reales, usar datos de ejemplo
            if not area_compliance:
                area_compliance = {
                    'Producción': {'SI': 18, 'NO': 3},
                    'Administración': {'SI': 8, 'NO': 1},
                    'Mantenimiento': {'SI': 5, 'NO': 2},
                    'Calidad': {'SI': 6, 'NO': 0},
                    'Logística': {'SI': 9, 'NO': 1}
                }
            
            areas = list(area_compliance.keys())
            si_values = [area_compliance[area]['SI'] for area in areas]
            no_values = [area_compliance[area]['NO'] for area in areas]
            
            # Crear gráfico de barras apiladas
            x = range(len(areas))
            
            bars1 = ax.bar(x, si_values, label='SI', color='#27ae60', alpha=0.8)
            bars2 = ax.bar(x, no_values, bottom=si_values, label='NO', color='#e74c3c', alpha=0.8)
            
            # Agregar valores en las barras
            for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
                # Valor SI
                height1 = bar1.get_height()
                if height1 > 0:
                    ax.text(bar1.get_x() + bar1.get_width()/2., height1/2,
                           f'{int(height1)}', ha='center', va='center', 
                           fontweight='bold', color='white', fontsize=9)
                
                # Valor NO
                height2 = bar2.get_height()
                if height2 > 0:
                    ax.text(bar2.get_x() + bar2.get_width()/2., height1 + height2/2,
                           f'{int(height2)}', ha='center', va='center', 
                           fontweight='bold', color='white', fontsize=9)
            
            ax.set_title('Cumplimiento de Turnos por Área', fontweight='bold', fontsize=14, pad=15)
            ax.set_xlabel('Área', fontweight='bold')
            ax.set_ylabel('Número de Empleados', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(areas, rotation=45, ha='right')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3, axis='y')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error cargando datos de cumplimiento\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)

    def get_produccion_data(self):
        """Obtener datos de producción desde la API"""
        try:
            response = requests.get('http://localhost:5000/get-produccion')
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error obteniendo datos de producción: {e}")
        return []

    def get_desperdicio_data(self):
        """Obtener datos de desperdicio desde la API"""
        try:
            response = requests.get('http://localhost:5000/get-desperdicios')
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error obteniendo datos de desperdicio: {e}")
        return []

    def get_empleados_data(self):
        """Obtener datos de empleados desde la API"""
        try:
            response = requests.get('http://localhost:5000/get-empleados')
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error obteniendo datos de empleados: {e}")
        return []

    def get_eventos_data(self):
        """Obtener datos de eventos desde la API"""
        try:
            response = requests.get('http://localhost:5000/get-eventos')
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error obteniendo datos de eventos: {e}")
        return []

class AttendanceControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_attendance()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Control de Asistencia")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabla de asistencia
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(5)
        self.attendance_table.setHorizontalHeaderLabels([
            "Empleado ID", "Nombre", "Evento", "Fecha/Hora", "Estado"
        ])
        header = self.attendance_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.attendance_table)
        self.setLayout(layout)

    def load_attendance(self):
        try:
            # Cargar eventos del día actual
            response = requests.get('http://localhost:5000/get-eventos')
            if response.status_code == 200:
                eventos = response.json()
                today = date.today().isoformat()
                eventos_hoy = [e for e in eventos if e.get('timestamp', '').startswith(today)]
                eventos_hoy.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                self.attendance_table.setRowCount(len(eventos_hoy))
                for row, evento in enumerate(eventos_hoy):
                    try:
                        timestamp = datetime.fromisoformat(evento.get('timestamp', ''))
                        formatted_time = timestamp.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        formatted_time = evento.get('timestamp', 'N/A')
                    
                    items = [
                        evento.get("EmpleadoID", "N/A"),
                        evento.get("username", "N/A"),
                        evento.get("evento", "N/A"),
                        formatted_time,
                        "✅ Registrado"
                    ]
                    
                    for col, text in enumerate(items):
                        item = QTableWidgetItem(str(text))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.attendance_table.setItem(row, col, item)
                        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando asistencia: {str(e)}")

class ConfigurationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Configuración del Sistema")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 30px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Secciones de configuración
        config_sections = QVBoxLayout()
        config_sections.setSpacing(20)

        # Configuración de horarios
        horarios_section = self.create_section("⏰ Configuración de Horarios", [
            "Hora inicio turno mañana: 08:00",
            "Hora fin turno mañana: 16:00",
            "Hora inicio turno tarde: 16:00",
            "Hora fin turno tarde: 00:00"
        ])
        config_sections.addLayout(horarios_section)

        # Configuración de notificaciones
        notif_section = self.create_section("🔔 Notificaciones", [
            "Notificar llegadas tardías: ✅ Activado",
            "Notificar ausencias: ✅ Activado",
            "Enviar reportes diarios: ✅ Activado"
        ])
        config_sections.addLayout(notif_section)

        # Configuración de seguridad
        security_section = self.create_section("🔒 Seguridad", [
            "Verificación facial: ✅ Obligatoria",
            "Tiempo de sesión: 8 horas",
            "Backup automático: ✅ Diario"
        ])
        config_sections.addLayout(security_section)

        layout.addLayout(config_sections)
        layout.addStretch()

        self.setLayout(layout)

    def create_section(self, title, items):
        section_layout = QVBoxLayout()
        
        # Título de la sección
        section_title = QLabel(title)
        section_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: rgba(52, 152, 219, 0.1);
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        section_layout.addWidget(section_title)
        
        # Items de configuración
        for item in items:
            item_label = QLabel(f"  • {item}")
            item_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #34495e;
                    padding: 5px 15px;
                    margin-left: 20px;
                }
            """)
            section_layout.addWidget(item_label)
        
        return section_layout

# -----------------------------
# PANELES ESPECÍFICOS PARA OPERARIOS
# -----------------------------
class ProductionControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_production_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Control de Producción")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Sección de métricas rápidas
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        # Tarjetas de métricas
        self.create_metric_card("Producción Hoy", "0 unidades", "#3498db", metrics_layout)
        self.create_metric_card("Eficiencia", "85%", "#27ae60", metrics_layout)
        self.create_metric_card("Defectos", "2", "#e74c3c", metrics_layout)
        
        layout.addLayout(metrics_layout)

        # Formulario para registrar producción
        form_layout = QVBoxLayout()
        form_section = QLabel("Registrar Producción")
        form_section.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        form_layout.addWidget(form_section)

        form_inputs = QFormLayout()
        self.producto_combo = QComboBox()
        # Cargar productos reales de la API
        self.load_products()
        
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setRange(1, 9999)
        self.cantidad_spin.setValue(1)
        
        self.turno_combo = QComboBox()
        self.turno_combo.addItems(["Mañana", "Tarde", "Noche"])
        
        # Aplicar estilos
        combo_style = """
            QComboBox, QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox:focus, QSpinBox:focus {
                border-color: #27ae60;
            }
        """
        self.producto_combo.setStyleSheet(combo_style)
        self.cantidad_spin.setStyleSheet(combo_style)
        self.turno_combo.setStyleSheet(combo_style)

        form_inputs.addRow("Producto:", self.producto_combo)
        form_inputs.addRow("Cantidad:", self.cantidad_spin)
        form_inputs.addRow("Turno:", self.turno_combo)

        self.btn_registrar = ModernButton("Registrar Producción", "success")
        self.btn_registrar.clicked.connect(self.registrar_produccion)

        form_layout.addLayout(form_inputs)
        form_layout.addWidget(self.btn_registrar)
        
        layout.addLayout(form_layout)

        # Tabla de producción del día
        table_title = QLabel("Producción del Día")
        table_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(table_title)

        self.production_table = QTableWidget()
        self.production_table.setColumnCount(5)
        self.production_table.setHorizontalHeaderLabels([
            "Hora", "Producto", "Cantidad", "Turno", "Operario"
        ])
        header = self.production_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.production_table)
        self.setLayout(layout)

    def load_products(self):
        """Cargar productos desde la API"""
        try:
            response = requests.get('http://localhost:5000/get-productos')
            if response.status_code == 200:
                productos = response.json()
                self.producto_combo.clear()
                for producto in productos:
                    nombre = producto.get('nombre', f"Producto {producto.get('id', 'N/A')}")
                    self.producto_combo.addItem(f"{nombre} (ID: {producto.get('id', 'N/A')})")
            else:
                # Fallback si la API no responde
                self.producto_combo.addItems(["Producto A", "Producto B", "Producto C", "Producto D"])
        except Exception as e:
            print(f"Error cargando productos: {e}")
            self.producto_combo.addItems(["Producto A", "Producto B", "Producto C", "Producto D"])

    def create_metric_card(self, title, value, color, parent_layout):
        """Crear tarjeta de métrica"""
        card = QWidget()
        card.setFixedHeight(100)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        parent_layout.addWidget(card)

    def registrar_produccion(self):
        """Registrar nueva producción"""
        try:
            production_data = {
                "producto": self.producto_combo.currentText(),
                "cantidad": self.cantidad_spin.value(),
                "turno": self.turno_combo.currentText(),
                "timestamp": datetime.now().isoformat(),
                "operario": "Usuario Actual"  # Aquí deberías usar el nombre del usuario actual
            }
            
            response = requests.post('http://localhost:5000/register-produccion', json=production_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Éxito", "Producción registrada correctamente.")
                self.load_production_data()
            else:
                QMessageBox.warning(self, "Error", "No se pudo registrar la producción.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error registrando producción: {str(e)}")

    def load_production_data(self):
        """Cargar datos de producción del día"""
        try:
            response = requests.get('http://localhost:5000/get-produccion')
            if response.status_code == 200:
                produccion_data = response.json()
                today = date.today().isoformat()
                produccion_hoy = [p for p in produccion_data if p.get('timestamp', '').startswith(today)]
                
                self.production_table.setRowCount(len(produccion_hoy))
                for row, prod in enumerate(produccion_hoy):
                    try:
                        timestamp = datetime.fromisoformat(prod.get('timestamp', ''))
                        formatted_time = timestamp.strftime('%H:%M')
                    except:
                        formatted_time = "N/A"
                    
                    items = [
                        formatted_time,
                        prod.get("producto", "N/A"),
                        str(prod.get("cantidad", 0)),
                        prod.get("turno", "N/A"),
                        prod.get("operario", "N/A")
                    ]
                    
                    for col, text in enumerate(items):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.production_table.setItem(row, col, item)
                        
        except Exception as e:
            print(f"Error cargando producción: {e}")

class InventoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_inventory()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Gestión de Inventario")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabla de inventario
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID Producto", "Nombre", "Stock Actual", "Stock Mínimo", "Estado"
        ])
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.inventory_table)

        # Botones de acción
        btn_layout = QHBoxLayout()
        self.btn_update_stock = ModernButton("Actualizar Stock", "primary")
        self.btn_add_product = ModernButton("Agregar Producto", "success")
        self.btn_refresh = ModernButton("Actualizar", "secondary")
        
        btn_layout.addWidget(self.btn_update_stock)
        btn_layout.addWidget(self.btn_add_product)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

        # Conectar botones
        self.btn_refresh.clicked.connect(self.load_inventory)
        
        self.setLayout(layout)

    def load_inventory(self):
        """Cargar inventario desde la API"""
        try:
            response = requests.get('http://localhost:5000/get-productos')
            if response.status_code == 200:
                products = response.json()
                
                self.inventory_table.setRowCount(len(products))
                for row, product in enumerate(products):
                    stock_actual = product.get("stock_actual", 0)
                    stock_minimo = product.get("stock_minimo", 0)
                    
                    # Determinar estado
                    if stock_actual <= stock_minimo:
                        estado = "🔴 Crítico"
                        color = "#e74c3c"
                    elif stock_actual <= stock_minimo * 1.5:
                        estado = "🟡 Bajo"
                        color = "#f39c12"
                    else:
                        estado = "🟢 Normal"
                        color = "#27ae60"
                    
                    items = [
                        str(product.get("id", "N/A")),
                        product.get("nombre", "N/A"),
                        str(stock_actual),
                        str(stock_minimo),
                        estado
                    ]
                    
                    for col, text in enumerate(items):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        
                        # Colorear la fila según el estado
                        if col == 4:  # Columna de estado
                            if "Crítico" in text:
                                item.setBackground(Qt.GlobalColor.red)
                                item.setForeground(Qt.GlobalColor.white)
                            elif "Bajo" in text:
                                item.setBackground(Qt.GlobalColor.yellow)
                            else:
                                item.setBackground(Qt.GlobalColor.green)
                                item.setForeground(Qt.GlobalColor.white)
                        
                        self.inventory_table.setItem(row, col, item)
                        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando inventario: {str(e)}")

class IncidentReportPanel(QWidget):
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Reportar Incidencia")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Formulario de reporte
        form_layout = QFormLayout()
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems([
            "Fallo de Equipo", "Problema de Calidad", "Seguridad", 
            "Mantenimiento", "Material Defectuoso", "Otro"
        ])
        
        self.prioridad_combo = QComboBox()
        self.prioridad_combo.addItems(["Baja", "Media", "Alta", "Crítica"])
        
        self.descripcion_text = QTextEdit()
        self.descripcion_text.setMaximumHeight(150)
        
        # Estilos
        widget_style = """
            QComboBox, QTextEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QComboBox:focus, QTextEdit:focus {
                border-color: #e74c3c;
            }
        """
        self.tipo_combo.setStyleSheet(widget_style)
        self.prioridad_combo.setStyleSheet(widget_style)
        self.descripcion_text.setStyleSheet(widget_style)
        
        form_layout.addRow("Tipo de Incidencia:", self.tipo_combo)
        form_layout.addRow("Prioridad:", self.prioridad_combo)
        form_layout.addRow("Descripción:", self.descripcion_text)
        
        layout.addLayout(form_layout)
        
        # Botón para enviar reporte
        self.btn_enviar = ModernButton("Enviar Reporte", "danger")
        self.btn_enviar.clicked.connect(self.enviar_reporte)
        layout.addWidget(self.btn_enviar)
        
        # Historial de reportes
        history_title = QLabel("Mis Reportes")
        history_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(history_title)
        
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(4)
        self.reports_table.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Prioridad", "Estado"
        ])
        header = self.reports_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.reports_table)
        
        self.setLayout(layout)
        self.load_user_reports()

    def enviar_reporte(self):
        """Enviar reporte de incidencia"""
        if not self.descripcion_text.toPlainText().strip():
            QMessageBox.warning(self, "Error", "Debe proporcionar una descripción de la incidencia.")
            return
            
        try:
            report_data = {
                "tipo": self.tipo_combo.currentText(),
                "prioridad": self.prioridad_combo.currentText(),
                "descripcion": self.descripcion_text.toPlainText().strip(),
                "empleado_id": self.usuario_data.get("EmpleadoID"),
                "empleado_nombre": f"{self.usuario_data.get('Nombre')} {self.usuario_data.get('Apellido')}",
                "timestamp": datetime.now().isoformat(),
                "estado": "Pendiente"
            }
            
            response = requests.post('http://localhost:5000/register-incidencia', json=report_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Éxito", "Incidencia reportada correctamente.")
                # Limpiar formulario
                self.descripcion_text.clear()
                self.load_user_reports()
            else:
                QMessageBox.warning(self, "Error", "No se pudo enviar el reporte.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error enviando reporte: {str(e)}")

    def load_user_reports(self):
        """Cargar reportes del usuario actual"""
        try:
            response = requests.get('http://localhost:5000/get-incidencias')
            if response.status_code == 200:
                incidencias = response.json()
                empleado_id = self.usuario_data.get("EmpleadoID")
                
                # Filtrar reportes del usuario actual
                user_reports = [r for r in incidencias if r.get("empleado_id") == empleado_id]
                user_reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                self.reports_table.setRowCount(len(user_reports))
                for row, report in enumerate(user_reports):
                    try:
                        timestamp = datetime.fromisoformat(report.get('timestamp', ''))
                        formatted_date = timestamp.strftime('%d/%m/%Y %H:%M')
                    except:
                        formatted_date = "N/A"
                    
                    items = [
                        formatted_date,
                        report.get("tipo", "N/A"),
                        report.get("prioridad", "N/A"),
                        report.get("estado", "Pendiente")
                    ]
                    
                    for col, text in enumerate(items):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.reports_table.setItem(row, col, item)
                        
        except Exception as e:
            print(f"Error cargando reportes del usuario: {e}")

class MyAttendancePanel(QWidget):
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.setup_ui()
        self.load_my_attendance()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Mi Asistencia")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Resumen de hoy
        today_section = QLabel("Resumen de Hoy")
        today_section.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px 0;")
        layout.addWidget(today_section)

        # Tarjetas de resumen
        summary_layout = QHBoxLayout()
        self.checkin_card = self.create_summary_card("Check-In", "No registrado", "#3498db")
        self.checkout_card = self.create_summary_card("Check-Out", "No registrado", "#e74c3c")
        self.horas_card = self.create_summary_card("Horas Trabajadas", "0:00", "#27ae60")
        
        summary_layout.addWidget(self.checkin_card)
        summary_layout.addWidget(self.checkout_card)
        summary_layout.addWidget(self.horas_card)
        
        layout.addLayout(summary_layout)

        # Historial de asistencia
        history_title = QLabel("Historial de Asistencia (Últimos 7 días)")
        history_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(history_title)

        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(4)
        self.attendance_table.setHorizontalHeaderLabels([
            "Fecha", "Check-In", "Check-Out", "Horas"
        ])
        header = self.attendance_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.attendance_table)
        self.setLayout(layout)

    def create_summary_card(self, title, value, color):
        # role_based_windows2.py - Continuación del código completado

        """Crear tarjeta de resumen"""
        card = QWidget()
        card.setFixedHeight(80)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card

    def load_my_attendance(self):
        """Cargar asistencia del usuario actual"""
        try:
            empleado_id = self.usuario_data.get("EmpleadoID")
            
            # Cargar eventos del empleado actual
            response = requests.get('http://localhost:5000/get-eventos')
            if response.status_code == 200:
                eventos = response.json()
                
                # Filtrar eventos del usuario actual
                my_eventos = [e for e in eventos if e.get("EmpleadoID") == empleado_id]
                
                # Procesar eventos por día
                from datetime import timedelta
                daily_attendance = defaultdict(lambda: {"checkin": None, "checkout": None})
                
                # Obtener últimos 7 días
                end_date = date.today()
                start_date = end_date - timedelta(days=7)
                
                for evento in my_eventos:
                    try:
                        timestamp = datetime.fromisoformat(evento.get('timestamp', ''))
                        day_key = timestamp.date().isoformat()
                        
                        # Solo procesar eventos de los últimos 7 días
                        if start_date <= timestamp.date() <= end_date:
                            if evento.get("evento") == "CheckIn":
                                daily_attendance[day_key]["checkin"] = timestamp
                            elif evento.get("evento") == "CheckOut":
                                daily_attendance[day_key]["checkout"] = timestamp
                    except:
                        continue
                
                # Actualizar tarjetas de resumen para hoy
                today_key = date.today().isoformat()
                if today_key in daily_attendance:
                    today_data = daily_attendance[today_key]
                    
                    if today_data["checkin"]:
                        checkin_time = today_data["checkin"].strftime('%H:%M')
                        self.update_card(self.checkin_card, "Check-In", checkin_time, "#27ae60")
                        
                    if today_data["checkout"]:
                        checkout_time = today_data["checkout"].strftime('%H:%M')
                        self.update_card(self.checkout_card, "Check-Out", checkout_time, "#27ae60")
                        
                        if today_data["checkin"]:
                            # Calcular horas trabajadas
                            worked_hours = today_data["checkout"] - today_data["checkin"]
                            hours = worked_hours.total_seconds() / 3600
                            formatted_hours = f"{int(hours)}:{int((hours % 1) * 60):02d}"
                            self.update_card(self.horas_card, "Horas Trabajadas", formatted_hours, "#27ae60")
                
                # Llenar tabla de historial
                sorted_days = sorted(daily_attendance.keys(), reverse=True)
                self.attendance_table.setRowCount(len(sorted_days))
                
                for row, day_key in enumerate(sorted_days):
                    day_data = daily_attendance[day_key]
                    
                    # Formatear fecha
                    try:
                        day_date = datetime.fromisoformat(day_key).strftime('%d/%m/%Y')
                    except:
                        day_date = day_key
                    
                    # Formatear check-in
                    checkin_str = day_data["checkin"].strftime('%H:%M') if day_data["checkin"] else "-"
                    
                    # Formatear check-out
                    checkout_str = day_data["checkout"].strftime('%H:%M') if day_data["checkout"] else "-"
                    
                    # Calcular horas
                    hours_str = "-"
                    if day_data["checkin"] and day_data["checkout"]:
                        worked_hours = day_data["checkout"] - day_data["checkin"]
                        hours = worked_hours.total_seconds() / 3600
                        hours_str = f"{int(hours)}:{int((hours % 1) * 60):02d}"
                    
                    items = [day_date, checkin_str, checkout_str, hours_str]
                    
                    for col, text in enumerate(items):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.attendance_table.setItem(row, col, item)
                        
        except Exception as e:
            print(f"Error cargando asistencia personal: {e}")

    def update_card(self, card, title, value, color):
        """Actualizar el contenido de una tarjeta"""
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        
        # Buscar y actualizar el label del valor
        for child in card.findChildren(QLabel):
            if child.font().pointSize() > 12:  # Es el label del valor
                child.setText(value)
            elif title in ["Check-In", "Check-Out", "Horas Trabajadas"]:
                if "Check-In" in child.text() or "Check-Out" in child.text() or "Horas Trabajadas" in child.text():
                    # Actualizar layout completo
                    layout = card.layout()
                    for i in range(layout.count()):
                        widget = layout.itemAt(i).widget()
                        if isinstance(widget, QLabel):
                            if "Check-In" in widget.text() and "Check-In" in title:
                                continue
                            elif "Check-Out" in widget.text() and "Check-Out" in title:
                                continue
                            elif "Horas" in widget.text() and "Horas" in title:
                                continue
                            else:
                                widget.setText(value)

# -----------------------------
# FUNCIONES AUXILIARES PARA LA API
# -----------------------------
def get_empleados_from_api():
    """Obtener empleados desde la API"""
    try:
        response = requests.get('http://localhost:5000/get-empleados')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error obteniendo empleados: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error de conexión obteniendo empleados: {e}")
        return []

def get_eventos_from_api():
    """Obtener eventos desde la API"""
    try:
        response = requests.get('http://localhost:5000/get-eventos')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error obteniendo eventos: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error de conexión obteniendo eventos: {e}")
        return []

def get_productos_from_api():
    """Obtener productos desde la API"""
    try:
        response = requests.get('http://localhost:5000/get-productos')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error obteniendo productos: {response.status_code}")
            # Fallback con productos por defecto
            return [
                {"id": 1, "nombre": "Producto A", "stock_actual": 100, "stock_minimo": 20},
                {"id": 2, "nombre": "Producto B", "stock_actual": 50, "stock_minimo": 15},
                {"id": 3, "nombre": "Producto C", "stock_actual": 75, "stock_minimo": 25}
            ]
    except Exception as e:
        print(f"Error de conexión obteniendo productos: {e}")
        # Fallback con productos por defecto
        return [
            {"id": 1, "nombre": "Producto A", "stock_actual": 100, "stock_minimo": 20},
            {"id": 2, "nombre": "Producto B", "stock_actual": 50, "stock_minimo": 15},
            {"id": 3, "nombre": "Producto C", "stock_actual": 75, "stock_minimo": 25}
        ]

def add_empleado_to_api(empleado_data):
    """Agregar empleado a la API"""
    try:
        response = requests.post('http://localhost:5000/add-empleado', json=empleado_data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error agregando empleado: {e}")
        return False

def update_empleado_in_api(empleado_id, empleado_data):
    """Actualizar empleado en la API"""
    try:
        response = requests.put(f'http://localhost:5000/update-empleado/{empleado_id}', json=empleado_data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error actualizando empleado: {e}")
        return False

def delete_empleado_from_api(empleado_id):
    """Eliminar empleado de la API"""
    try:
        response = requests.delete(f'http://localhost:5000/delete-empleado/{empleado_id}')
        return response.status_code == 200
    except Exception as e:
        print(f"Error eliminando empleado: {e}")
        return False

def register_produccion_to_api(produccion_data):
    """Registrar producción en la API"""
    try:
        response = requests.post('http://localhost:5000/register-produccion', json=produccion_data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error registrando producción: {e}")
        return False

def get_produccion_from_api():
    """Obtener datos de producción desde la API"""
    try:
        response = requests.get('http://localhost:5000/get-produccion')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error obteniendo producción: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error de conexión obteniendo producción: {e}")
        return []

def register_incidencia_to_api(incidencia_data):
    """Registrar incidencia en la API"""
    try:
        response = requests.post('http://localhost:5000/register-incidencia', json=incidencia_data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error registrando incidencia: {e}")
        return False

def get_incidencias_from_api():
    """Obtener incidencias desde la API"""
    try:
        response = requests.get('http://localhost:5000/get-incidencias')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error obteniendo incidencias: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error de conexión obteniendo incidencias: {e}")
        return []

def register_evento_to_api(evento_data):
    """Registrar evento en la API"""
    try:
        response = requests.post('http://localhost:5000/register-evento', json=evento_data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error registrando evento: {e}")
        return False

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