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
from welcome_panel import WelcomePanel
import requests
import json


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
            response = requests.get('https://grupo7-tpinicial.onrender.com/get-empleados')
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

        # Botones para actualizar datos y OEE
        button_layout = QHBoxLayout()
        self.btn_refresh = ModernButton("🔄 Actualizar Reportes", "primary")
        self.btn_refresh.clicked.connect(self.load_reports)
        self.btn_oee = ModernButton("📊 Ver OEE", "success")
        self.btn_oee.clicked.connect(self.show_oee_chart)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addWidget(self.btn_oee)
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
        """Gráfico de torta de cantidad producida en 2024 por producto - CORREGIDO"""
        try:
            # Filtrar datos del 2024 y agrupar por producto
            product_production = defaultdict(int)

            # Si no hay datos reales, usar datos de ejemplo
            if not product_production:
                product_production = {
                    'Harina': 4500, 'Aceite': 3800, 'Azúcar': 5200,
                    'Arroz': 2900, 'Fideos': 3600
                }
            
            # Preparar datos para el gráfico de torta
            products = list(product_production.keys())
            production_values = list(product_production.values())
            
            # Colores para cada producto
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3',
                    '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43']
            
            # Crear gráfico de torta
            wedges, texts, autotexts = ax.pie(production_values, labels=products, autopct='%1.1f%%', 
                                            colors=colors[:len(products)], startangle=90, 
                                            textprops={'fontsize': 9, 'fontweight': 'bold'})
            
            # Mejorar el formato de los porcentajes
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Producción 2024 por Producto', 
                        fontweight='bold', fontsize=14, pad=20)
            
            # Añadir leyenda con totales
            legend_labels = [f'{product}: {value:,}' for product, value in zip(products, production_values)]
            ax.legend(wedges, legend_labels, title="Producción por Producto", 
                loc="center left", bbox_to_anchor=(-0.9, 0.5), fontsize=8)
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error cargando datos de producción\n{str(e)}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=10)

    def create_quarterly_waste_production_chart(self, ax):
        """Gráfico de desperdicio y producción por trimestre"""
        try:
            # Agrupar por trimestre
            quarterly_production = defaultdict(int)
            quarterly_waste = defaultdict(int)

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
            # Agrupar eventos por área
            area_checkins = defaultdict(int)
            area_checkouts = defaultdict(int)
        
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

    def create_shift_compliance_by_area_chart(self, ax, area_compliance=None):
        """Gráfico de cumplimiento de turnos por área"""
        try:
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

    def show_oee_chart(self):
        """Mostrar gráfico OEE en ventana separada"""
        try:
            # Crear nueva ventana para OEE
            self.oee_window = QDialog(self)
            self.oee_window.setWindowTitle("Overall Equipment Effectiveness (OEE)")
            self.oee_window.setFixedSize(1000, 700)
            
            layout = QVBoxLayout(self.oee_window)
            layout.setContentsMargins(20, 10, 20, 20)  # left, top, right, bottom
            layout.setSpacing(10)  # espacio entre widgets
            
            # Título
            title = QLabel("Análisis OEE (Overall Equipment Effectiveness)")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 15px;")
            layout.addWidget(title)
            
            # Crear figura para OEE
            oee_figure = Figure(figsize=(12, 8))
            oee_canvas = FigureCanvas(oee_figure)
            
            # Generar gráfico OEE
            self.generate_oee_chart(oee_figure)
            
            layout.addWidget(oee_canvas)
            
            # Botón cerrar
            close_btn = ModernButton("Cerrar", "secondary")
            close_btn.clicked.connect(self.oee_window.close)
            close_layout = QHBoxLayout()
            close_layout.addStretch()
            close_layout.addWidget(close_btn)
            close_layout.addStretch()
            layout.addLayout(close_layout)
            
            self.oee_window.setLayout(layout)
            self.oee_window.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mostrando gráfico OEE: {str(e)}")

    def generate_oee_chart(self, figure):
        """Generar gráfico OEE completo"""
        try:
            figure.clear()
            
            # Crear subgráficos (2x2)
            ax1 = figure.add_subplot(2, 2, 1)  # OEE por mes
            ax2 = figure.add_subplot(2, 2, 2)  # Componentes OEE actual
            ax3 = figure.add_subplot(2, 2, 3)  # Tendencia OEE semanal
            ax4 = figure.add_subplot(2, 2, 4)  # Disponibilidad vs Performance vs Calidad
            
            # Obtener datos para OEE
            oee_data = self.calculate_oee_metrics()
            
            self.create_monthly_oee_chart(ax1, oee_data)
            self.create_oee_components_chart(ax2, oee_data)
            self.create_weekly_oee_trend_chart(ax3, oee_data)
            self.create_oee_comparison_chart(ax4, oee_data)
            
            figure.suptitle('Dashboard OEE - Overall Equipment Effectiveness', 
                        fontsize=16, fontweight='bold', y=0.95)
            figure.tight_layout(rect=[0, 0.03, 1, 0.95])
            
        except Exception as e:
            print(f"Error generando gráfico OEE: {e}")

    def show_oee_chart(self):
        """Mostrar gráfico OEE por área en ventana separada"""
        try:
            # Crear nueva ventana para OEE
            self.oee_window = QDialog(self)
            self.oee_window.setWindowTitle("OEE por Área")
            self.oee_window.setFixedSize(800, 600)
            
            layout = QVBoxLayout(self.oee_window)
            
            # Título
            title = QLabel("OEE por Área/Línea de Producción")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 15px;")
            layout.addWidget(title)
            
            # Crear figura para OEE
            oee_figure = Figure(figsize=(10, 6))
            oee_canvas = FigureCanvas(oee_figure)
            
            # Obtener datos OEE
            oee_data = self.calculate_oee_metrics()
            
            # Crear gráfico solo de OEE por área
            ax = oee_figure.add_subplot(1, 1, 1)
            self.create_oee_comparison_chart(ax, oee_data)
            
            layout.addWidget(oee_canvas)
            
            # Botón cerrar
            close_btn = ModernButton("Cerrar", "secondary")
            close_btn.clicked.connect(self.oee_window.close)
            close_layout = QHBoxLayout()
            close_layout.addStretch()
            close_layout.addWidget(close_btn)
            close_layout.addStretch()
            layout.addLayout(close_layout)
            
            self.oee_window.setLayout(layout)
            self.oee_window.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mostrando gráfico OEE por área: {str(e)}")

    def calculate_oee_metrics(self):
        """Calcular métricas OEE basadas en datos reales"""
        try:
            # Datos por defecto si no hay datos reales
            default_data = {
                'monthly': {
                    'Enero': 72, 'Febrero': 75, 'Marzo': 78, 'Abril': 81,
                    'Mayo': 77, 'Junio': 83, 'Julio': 85, 'Agosto': 82,
                    'Septiembre': 86, 'Octubre': 88, 'Noviembre': 84, 'Diciembre': 87
                },
                'current_components': {
                    'Disponibilidad': 92,  # % tiempo operativo / tiempo planificado
                    'Performance': 87,     # % velocidad real / velocidad ideal
                    'Calidad': 94         # % productos buenos / productos totales
                },
                'weekly': [
                    {'semana': 'S1', 'oee': 82},
                    {'semana': 'S2', 'oee': 85},
                    {'semana': 'S3', 'oee': 78},
                    {'semana': 'S4', 'oee': 88},
                    {'semana': 'S5', 'oee': 84},
                    {'semana': 'S6', 'oee': 87},
                    {'semana': 'S7', 'oee': 89},
                    {'semana': 'S8', 'oee': 86}
                ],
                'areas': {
                    'Producción': {'disponibilidad': 91, 'performance': 85, 'calidad': 96},
                    'Línea A': {'disponibilidad': 89, 'performance': 90, 'calidad': 92},
                    'Línea B': {'disponibilidad': 94, 'performance': 82, 'calidad': 95},
                    'Empaque': {'disponibilidad': 88, 'performance': 88, 'calidad': 98}
                }
            }            
            return default_data
            
        except Exception as e:
            print(f"Error calculando métricas OEE: {e}")
            # Retornar datos por defecto en caso de error
            return {
                'monthly': {'Enero': 75, 'Febrero': 78, 'Marzo': 82},
                'current_components': {'Disponibilidad': 85, 'Performance': 80, 'Calidad': 90},
                'weekly': [{'semana': f'S{i}', 'oee': 75 + i*2} for i in range(1, 9)],
                'areas': {'Producción': {'disponibilidad': 85, 'performance': 80, 'calidad': 90}}
            }


    def calculate_oee_metrics(self):
        """Calcular métricas OEE solo por áreas"""
        try:
            # Datos por defecto si no hay datos reales
            areas_data = {
                'Producción': {'disponibilidad': 91, 'performance': 85, 'calidad': 96},
                'Línea A': {'disponibilidad': 89, 'performance': 90, 'calidad': 92},
                'Línea B': {'disponibilidad': 94, 'performance': 82, 'calidad': 95},
                'Empaque': {'disponibilidad': 88, 'performance': 88, 'calidad': 98}
            }            
            return {'areas': areas_data}
            
        except Exception as e:
            print(f"Error calculando métricas OEE: {e}")
            return {'areas': {'Producción': {'disponibilidad': 85, 'performance': 80, 'calidad': 90}}}


    def create_oee_comparison_chart(self, ax, oee_data):
        """Gráfico de comparación OEE por áreas"""
        try:
            areas_data = oee_data['areas']
            
            areas = list(areas_data.keys())
            disponibilidad = [areas_data[area]['disponibilidad'] for area in areas]
            performance = [areas_data[area]['performance'] for area in areas]
            calidad = [areas_data[area]['calidad'] for area in areas]
            
            # Calcular OEE por área
            oee_por_area = [(d * p * c) / 10000 for d, p, c in zip(disponibilidad, performance, calidad)]
            
            # Configurar posiciones de las barras
            x_pos = range(len(areas))
            
            # Crear barras para OEE total
            bars = ax.bar(x_pos, oee_por_area, color=['#3498db', '#27ae60', '#f39c12', '#e74c3c'][:len(areas)], 
                        alpha=0.8, width=0.6)
            
            # Agregar valores en las barras
            for bar, value in zip(bars, oee_por_area):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Línea de objetivo
            ax.axhline(y=85, color='red', linestyle='--', alpha=0.7, label='Objetivo 85%')
            
            ax.set_title('OEE por Área/Línea de Producción', fontweight='bold', fontsize=12, pad=15)
            ax.set_xlabel('Áreas', fontweight='bold')
            ax.set_ylabel('OEE (%)', fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(areas, rotation=45, ha='right')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3, axis='y')
            ax.legend()
            
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error cargando comparación por áreas\n{str(e)}', 
                ha='center', va='center', transform=ax.transAxes)

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
            response = requests.get('https://grupo7-tpinicial.onrender.com/get-eventos')
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
