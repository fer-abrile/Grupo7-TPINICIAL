from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from datetime import datetime, date
from collections import defaultdict
from modern_components import ModernButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import requests

# -----------------------------
# PANEL DE BIENVENIDA
# -----------------------------
class WelcomePanel(QWidget):
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_label = QLabel(f"¡Bienvenido al Sistema!")
        welcome_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        user_label = QLabel(f"{self.usuario_data.get('Nombre', '')} {self.usuario_data.get('Apellido', '')}")
        user_label.setStyleSheet("font-size: 24px; color: #34495e; margin-bottom: 30px;")
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_label = QLabel("Selecciona una opción del panel lateral para comenzar")
        info_label.setStyleSheet("font-size: 16px; color: #7f8c8d; font-style: italic;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(welcome_label)
        layout.addWidget(user_label)
        layout.addWidget(info_label)

        self.setLayout(layout)

# -----------------------------
# PANEL DE GRAFICOS
# -----------------------------
class GraphicsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Gráficos de Asistencia")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.figure = Figure(figsize=(10,6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def load_data(self):
        try:
            today = date.today().isoformat()
            response = requests.get('http://localhost:5000/get-eventos')
            checkin_data = []
            checkout_data = []
            if response.status_code == 200:
                eventos = response.json()
                for data in eventos:
                    if data.get("timestamp", "").startswith(today):
                        if data.get("evento") == "CheckIn":
                            checkin_data.append(data)
                        elif data.get("evento") == "CheckOut":
                            checkout_data.append(data)
            self.create_chart(checkin_data, checkout_data)
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.create_empty_chart()

    def create_chart(self, checkin_data, checkout_data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        checkin_hours = defaultdict(int)
        checkout_hours = defaultdict(int)

        for e in checkin_data:
            try:
                timestamp = datetime.fromisoformat(e['timestamp'])
                checkin_hours[timestamp.hour] += 1
            except: continue

        for e in checkout_data:
            try:
                timestamp = datetime.fromisoformat(e['timestamp'])
                checkout_hours[timestamp.hour] += 1
            except: continue

        hours = range(24)
        checkin_counts = [checkin_hours[h] for h in hours]
        checkout_counts = [checkout_hours[h] for h in hours]

        width = 0.35
        x_pos = range(24)
        bars1 = ax.bar([x - width/2 for x in x_pos], checkin_counts, width, label='Check-In', color='#27ae60', alpha=0.8)
        bars2 = ax.bar([x + width/2 for x in x_pos], checkout_counts, width, label='Check-Out', color='#e74c3c', alpha=0.8)

        ax.set_xlabel("Hora del día")
        ax.set_ylabel("Cantidad de eventos")
        ax.set_title(f"Check-In/Check-Out - {date.today().strftime('%d/%m/%Y')}")
        ax.set_xticks(x_pos)
        ax.set_xticklabels([f"{h:02d}:00" for h in hours], rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)

        for bar in bars1 + bars2:
            if bar.get_height() > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height()+0.05, str(int(bar.get_height())), ha='center', va='bottom', fontsize=8)

        self.canvas.draw()

    def create_empty_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5,0.5,"No hay datos para mostrar hoy", ha='center', va='center', transform=ax.transAxes, fontsize=16)
        self.canvas.draw()

# -----------------------------
# PANEL DE EMPLEADOS
# -----------------------------
class EmployeePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Lista de Empleados Registrados")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID Empleado","Nombre","Apellido","Área","Puesto","Turno","Fecha Ingreso","Username"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_employees(self):
        try:
            response = requests.get('http://localhost:5000/get-empleados')
            empleados = response.json() if response.status_code == 200 else []
            self.table.setRowCount(len(empleados))
            for row, emp in enumerate(empleados):
                items = [
                    emp.get("EmpleadoID","N/A"),
                    emp.get("Nombre","N/A"),
                    emp.get("Apellido","N/A"),
                    emp.get("Area","N/A"),
                    emp.get("Puesto","N/A"),
                    emp.get("Turno","N/A"),
                    emp.get("FechaIngreso","N/A"),
                    emp.get("username","N/A")
                ]
                for col, text in enumerate(items):
                    item = QTableWidgetItem(str(text))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
        except Exception as e:
            print(f"Error cargando empleados: {e}")

# -----------------------------
# PANEL MULTI-GRAFICOS
# -----------------------------
class MultiChartsPanel(QWidget):
    """Panel con los 3 gráficos extra: por producto, materia prima y empleados por área"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20,20,20,20)
        self.figure = Figure(figsize=(12,8))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def load_data(self):
        try:
            self.figure.clear()
            ax1 = self.figure.add_subplot(311)
            ax2 = self.figure.add_subplot(312)
            ax3 = self.figure.add_subplot(313)

            productos_count = defaultdict(int)
            materias_count = defaultdict(int)
            area_count = defaultdict(int)

            # Productos
            r_prod = requests.get('http://localhost:5000/get-productos')
            if r_prod.status_code == 200:
                for data in r_prod.json():
                    producto_id = data.get("id")
                    stock_actual = data.get("stock_actual")
                    if producto_id is not None and stock_actual is not None:
                        productos_count[producto_id] = stock_actual

            # Empleados
            r_emp = requests.get('http://localhost:5000/get-fake-empleados')
            if r_emp.status_code == 200:
                for data in r_emp.json():
                    area = data.get("Area")
                    if area: area_count[area] +=1

            # Materia Prima
            r_mat = requests.get('http://localhost:5000/get-materias')
            if r_mat.status_code == 200:
                for data in r_mat.json():
                    materia = data.get("id")
                    stock_actual = data.get("stock_actual")
                    if materia is not None and stock_actual is not None:
                        materias_count[materia] = stock_actual

            # Gráfico 1: Productos
            ax1.bar(productos_count.keys(), productos_count.values(), color="#3498db", alpha=0.8)
            ax1.set_title("Stock actual por Producto")
            ax1.set_xlabel("ID Producto")
            ax1.set_ylabel("Stock Actual")

            # Gráfico 2: Materias primas
            ax2.bar(materias_count.keys(), materias_count.values(), color="#2ecc71", alpha=0.8)
            ax2.set_title("Recuento por Materia Prima")

            # Gráfico 3: Empleados por área
            ax3.bar(area_count.keys(), area_count.values(), color="#e74c3c", alpha=0.8)
            ax3.set_title("Empleados por Área")

            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Error cargando multi-graficos: {e}")

# -----------------------------
# MAIN WINDOW
# -----------------------------
class MainWindow(QMainWindow):
    def __init__(self, usuario_data):
        super().__init__()
        self.usuario_data = usuario_data
        self.setWindowTitle("Sistema de Gestión de Empleados")
        self.setFixedSize(1200, 800)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # ---------------- Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20,30,20,30)
        sidebar_layout.setSpacing(15)

        panel_title = QLabel("Panel de Control")
        panel_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(panel_title)

        self.btn_inicio = ModernButton("🏠 Inicio", "secondary")
        self.btn_graficos = ModernButton("📊 CheckIn/Out", "primary")
        self.btn_empleados = ModernButton("👥 Empleados", "success")
        self.btn_multicharts = ModernButton("📈 Otros Gráficos", "warning")
        self.btn_salir = ModernButton("🚪 Salir", "danger")

        sidebar_layout.addWidget(self.btn_inicio)
        sidebar_layout.addWidget(self.btn_graficos)
        sidebar_layout.addWidget(self.btn_empleados)
        sidebar_layout.addWidget(self.btn_multicharts)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_salir)

        sidebar.setLayout(sidebar_layout)

        # ---------------- Contenido
        self.content_area = QStackedWidget()
        self.welcome_panel = WelcomePanel(self.usuario_data)
        self.graphics_panel = GraphicsPanel()
        self.employee_panel = EmployeePanel()
        self.multi_charts_panel = MultiChartsPanel()

        self.content_area.addWidget(self.welcome_panel)     # 0
        self.content_area.addWidget(self.graphics_panel)    # 1
        self.content_area.addWidget(self.employee_panel)    # 2
        self.content_area.addWidget(self.multi_charts_panel) # 3

        self.content_area.setCurrentIndex(0)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area,1)
        central_widget.setLayout(main_layout)

        # Conexiones botones
        self.btn_inicio.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        self.btn_graficos.clicked.connect(lambda: self.content_area.setCurrentIndex(1))
        self.btn_empleados.clicked.connect(lambda: self.content_area.setCurrentIndex(2))
        self.btn_multicharts.clicked.connect(lambda: self.content_area.setCurrentIndex(3))
        self.btn_salir.clicked.connect(self.realizar_checkout)

    def realizar_checkout(self):
        """Checkout manual desde el botón Salir"""
        checkout_data = {
            "EmpleadoID": self.usuario_data.get("EmpleadoID"),
            "username": self.usuario_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckOut"
        }
        try:
            response = requests.post('http://localhost:5000/register-evento', json=checkout_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Salida", "Se ha registrado el CheckOut correctamente.")
                self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar checkout: {str(e)}")

# -----------------------------
# VENTANA PARA EMPLEADOS TEMPORALES
# -----------------------------
class TemporalWindow(QMainWindow):
    def __init__(self, usuario_data):
        super().__init__()
        self.usuario_data = usuario_data
        self.setWindowTitle("Sistema de Gestión - Empleado Temporal")
        self.setFixedSize(1000, 700)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # ---------------- Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-right: 2px solid #2c3e50;
            }
        """)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20,30,20,30)
        sidebar_layout.setSpacing(15)

        # Título del panel
        panel_title = QLabel("Panel Temporal")
        panel_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 10px;
                background-color: #e67e22;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        sidebar_layout.addWidget(panel_title)

        # Botones de navegación
        self.btn_perfil = ModernButton("👤 Mi Perfil", "primary")
        self.btn_asistencia = ModernButton("⏰ Asistencias", "success")
        self.btn_manual = ModernButton("📖 Manual", "warning")
        self.btn_contacto = ModernButton("📞 Contacto", "info")
        self.btn_salir = ModernButton("🚪 Salir", "danger")

        sidebar_layout.addWidget(self.btn_perfil)
        sidebar_layout.addWidget(self.btn_asistencia)
        sidebar_layout.addWidget(self.btn_manual)
        sidebar_layout.addWidget(self.btn_contacto)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_salir)

        sidebar.setLayout(sidebar_layout)

        # ---------------- Contenido
        self.content_area = QStackedWidget()
        
        # Crear paneles
        self.perfil_panel = self.create_perfil_panel()
        self.asistencia_panel = self.create_asistencia_panel()
        self.manual_panel = self.create_manual_panel()
        self.contacto_panel = self.create_contacto_panel()

        self.content_area.addWidget(self.perfil_panel)     # 0
        self.content_area.addWidget(self.asistencia_panel)  # 1
        self.content_area.addWidget(self.manual_panel)      # 2
        self.content_area.addWidget(self.contacto_panel)    # 3

        self.content_area.setCurrentIndex(0)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area, 1)
        central_widget.setLayout(main_layout)

        # Conexiones de botones
        self.btn_perfil.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        self.btn_asistencia.clicked.connect(lambda: self.content_area.setCurrentIndex(1))
        self.btn_manual.clicked.connect(lambda: self.content_area.setCurrentIndex(2))
        self.btn_contacto.clicked.connect(lambda: self.content_area.setCurrentIndex(3))
        self.btn_salir.clicked.connect(self.realizar_checkout)

    def create_perfil_panel(self):
        """Panel de información personal"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Título
        title = QLabel("Mi Información Personal")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-bottom: 20px;
            text-align: center;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Card de información
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout()

        # Estado temporal destacado (versión compacta)
        temporal_status = QLabel("🔸 TEMPORAL")
        temporal_status.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: #e67e22;
                padding: 12px 8px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 20px;
                min-height: 30px;
            }
        """)
        temporal_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temporal_status.setWordWrap(True)
        info_layout.addWidget(temporal_status)

        # Información personal
        info_data = [
            ("Nombre Completo", f"{self.usuario_data.get('Nombre', '')} {self.usuario_data.get('Apellido', '')}"),
            ("Legajo", self.usuario_data.get('EmpleadoID', 'N/A')),
            ("Puesto", self.usuario_data.get('Puesto', 'N/A')),
            ("Área", self.usuario_data.get('Area', 'N/A')),
            ("Turno", self.usuario_data.get('Turno', 'N/A')),
            ("Fecha de Ingreso", self.usuario_data.get('FechaIngreso', 'N/A')),
            ("Usuario", self.usuario_data.get('username', 'N/A'))
        ]

        for label_text, value in info_data:
            row_layout = QHBoxLayout()
            
            label = QLabel(f"{label_text}:")
            label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #34495e;
                    min-width: 150px;
                }
            """)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #2c3e50;
                    padding: 8px;
                    background-color: #ecf0f1;
                    border-radius: 5px;
                }
            """)
            
            row_layout.addWidget(label)
            row_layout.addWidget(value_label)
            row_layout.addStretch()
            
            info_layout.addLayout(row_layout)

        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_asistencia_panel(self):
        """Panel de asistencias con check-in/out y historial personal"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Título
        title = QLabel("Mis Asistencias")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #2c3e50; 
            text-align: center;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Botones de check-in/out
        buttons_layout = QHBoxLayout()
        
        self.btn_checkin = ModernButton("📍 CHECK-IN", "success")
        self.btn_checkin.setMinimumHeight(60)
        self.btn_checkin.clicked.connect(self.realizar_checkin)
        
        self.btn_checkout = ModernButton("📤 CHECK-OUT", "danger")
        self.btn_checkout.setMinimumHeight(60)
        self.btn_checkout.clicked.connect(self.realizar_checkout_manual)
        
        buttons_layout.addWidget(self.btn_checkin)
        buttons_layout.addWidget(self.btn_checkout)
        layout.addLayout(buttons_layout)

        # Tabla de historial personal
        history_title = QLabel("Mi Historial de Asistencias")
        history_title.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin: 20px 0 10px 0;
        """)
        layout.addWidget(history_title)

        self.asistencia_table = QTableWidget()
        self.asistencia_table.setColumnCount(4)
        self.asistencia_table.setHorizontalHeaderLabels([
            "Fecha", "Check-In", "Check-Out", "Horas"
        ])
        
        header = self.asistencia_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.asistencia_table.setAlternatingRowColors(True)
        
        self.asistencia_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 12px;
            }
        """)
        
        layout.addWidget(self.asistencia_table)
        
        # Cargar historial al crear el panel
        self.load_my_attendance()
        
        widget.setLayout(layout)
        return widget

    def create_manual_panel(self):
        """Panel con manual de normas"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        # Título
        title = QLabel("Manual de Normas y Procedimientos")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #2c3e50; 
            text-align: center;
            margin-bottom: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Contenido del manual en un scroll area
        from PyQt6.QtWidgets import QScrollArea, QTextEdit
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        manual_text = QTextEdit()
        manual_text.setReadOnly(True)
        manual_text.setHtml("""
        <div style="font-family: Arial; line-height: 1.6; padding: 20px;">
            <h2 style="color: #e74c3c;">🔒 NORMAS DE SEGURIDAD</h2>
            <ul>
                <li>Usar siempre el equipo de protección personal asignado</li>
                <li>Reportar inmediatamente cualquier incidente o situación peligrosa</li>
                <li>Mantener el área de trabajo limpia y ordenada</li>
                <li>No operar equipos sin la capacitación adecuada</li>
                <li>Respetar las señalizaciones de seguridad</li>
            </ul>
            
            <h2 style="color: #3498db;">✅ NORMAS DE CALIDAD</h2>
            <ul>
                <li>Seguir los procedimientos establecidos para cada tarea</li>
                <li>Verificar la calidad del trabajo antes de considerarlo terminado</li>
                <li>Reportar cualquier defecto o problema de calidad</li>
                <li>Mantener los estándares de higiene requeridos</li>
                <li>Documentar las actividades según los protocolos</li>
            </ul>
            
            <h2 style="color: #27ae60;">🤝 NORMAS DE CONDUCTA</h2>
            <ul>
                <li>Mantener un trato respetuoso con compañeros y supervisores</li>
                <li>Cumplir puntualmente con los horarios establecidos</li>
                <li>Comunicar con anticipación cualquier ausencia</li>
                <li>Mantener la confidencialidad de la información de la empresa</li>
                <li>Usar apropiadamente los recursos y equipos de la empresa</li>
            </ul>
            
            <h2 style="color: #f39c12;">⚠️ IMPORTANTES PARA TEMPORALES</h2>
            <ul>
                <li>Su contrato tiene duración limitada según lo acordado</li>
                <li>Debe registrar asistencia diariamente (check-in/out)</li>
                <li>Cualquier duda consultar con su supervisor inmediato</li>
                <li>Al finalizar el contrato, devolver todos los elementos asignados</li>
            </ul>
        </div>
        """)
        
        scroll_area.setWidget(manual_text)
        layout.addWidget(scroll_area)
        
        widget.setLayout(layout)
        return widget

    def create_contacto_panel(self):
        """Panel de contacto con supervisor"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Título
        title = QLabel("Contacto con Supervisor")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #2c3e50; 
            text-align: center;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Card de información del supervisor
        supervisor_frame = QFrame()
        supervisor_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        supervisor_layout = QVBoxLayout()

        # Información del supervisor (simulada)
        supervisor_info = QLabel("""
        <div style="text-align: center;">
            <h2 style="color: #2c3e50;">👨‍💼 Supervisor Inmediato</h2>
            <p style="font-size: 18px; color: #34495e;"><strong>Ing. Carlos Mendoza</strong></p>
            <p style="font-size: 16px; color: #7f8c8d;">Jefe de Área - Producción</p>
            <br>
            <p style="font-size: 16px;"><strong>📧 Email:</strong> carlos.mendoza@empresa.com</p>
            <p style="font-size: 16px;"><strong>📱 Teléfono:</strong> +54 11 1234-5678</p>
            <p style="font-size: 16px;"><strong>📍 Oficina:</strong> Edificio A - Planta Baja - Of. 105</p>
            <p style="font-size: 16px;"><strong>⏰ Horario:</strong> Lunes a Viernes 8:00 - 17:00</p>
        </div>
        """)
        supervisor_info.setStyleSheet("padding: 20px;")
        supervisor_layout.addWidget(supervisor_info)

        # Botón de contacto rápido
        contact_button = ModernButton("📞 Llamar Ahora", "primary")
        contact_button.setMinimumHeight(50)
        contact_button.clicked.connect(lambda: QMessageBox.information(
            self, "Contacto", 
            "En un entorno real, esto abriría la aplicación de teléfono\n"
            "o un sistema de comunicación interna."
        ))
        supervisor_layout.addWidget(contact_button)

        supervisor_frame.setLayout(supervisor_layout)
        layout.addWidget(supervisor_frame)

        # Información adicional
        info_adicional = QLabel("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;">
            <h3 style="color: #495057;">ℹ️ Información Importante:</h3>
            <ul style="color: #6c757d;">
                <li>Para emergencias fuera del horario, contactar seguridad: Ext. 911</li>
                <li>Para temas administrativos: RRHH Ext. 100</li>
                <li>Para problemas técnicos: Soporte TI Ext. 200</li>
            </ul>
        </div>
        """)
        layout.addWidget(info_adicional)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def realizar_checkin(self):
        """Registrar check-in"""
        checkin_data = {
            "EmpleadoID": self.usuario_data.get("EmpleadoID"),
            "username": self.usuario_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckIn"
        }
        try:
            response = requests.post('http://localhost:5000/register-evento', json=checkin_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Check-In", "Check-In registrado correctamente.")
                self.load_my_attendance()  # Recargar historial
            else:
                QMessageBox.warning(self, "Error", "No se pudo registrar el Check-In.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar Check-In: {str(e)}")

    def realizar_checkout_manual(self):
        """Registrar check-out manual"""
        checkout_data = {
            "EmpleadoID": self.usuario_data.get("EmpleadoID"),
            "username": self.usuario_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckOut"
        }
        try:
            response = requests.post('http://localhost:5000/register-evento', json=checkout_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Check-Out", "Check-Out registrado correctamente.")
                self.load_my_attendance()  # Recargar historial
            else:
                QMessageBox.warning(self, "Error", "No se pudo registrar el Check-Out.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar Check-Out: {str(e)}")

    def load_my_attendance(self):
        """Cargar historial de asistencia personal"""
        try:
            empleado_id = self.usuario_data.get("EmpleadoID")
            response = requests.get('http://localhost:5000/get-eventos')
            
            if response.status_code == 200:
                eventos = response.json()
                my_eventos = [e for e in eventos if e.get("EmpleadoID") == empleado_id]
                
                # Procesar eventos por día
                daily_attendance = defaultdict(lambda: {"checkin": None, "checkout": None})
                
                for evento in my_eventos:
                    try:
                        timestamp = datetime.fromisoformat(evento.get('timestamp', ''))
                        day_key = timestamp.date().isoformat()
                        
                        if evento.get("evento") == "CheckIn":
                            if not daily_attendance[day_key]["checkin"] or timestamp > daily_attendance[day_key]["checkin"]:
                                daily_attendance[day_key]["checkin"] = timestamp
                        elif evento.get("evento") == "CheckOut":
                            if not daily_attendance[day_key]["checkout"] or timestamp > daily_attendance[day_key]["checkout"]:
                                daily_attendance[day_key]["checkout"] = timestamp
                    except:
                        continue
                
                # Llenar tabla
                sorted_days = sorted(daily_attendance.keys(), reverse=True)[:14]  # Últimos 14 días
                self.asistencia_table.setRowCount(len(sorted_days))
                
                for row, day_key in enumerate(sorted_days):
                    day_data = daily_attendance[day_key]
                    
                    # Formatear fecha
                    try:
                        formatted_date = datetime.fromisoformat(day_key).strftime('%d/%m/%Y')
                    except:
                        formatted_date = day_key
                    
                    checkin_str = day_data["checkin"].strftime('%H:%M') if day_data["checkin"] else "-"
                    checkout_str = day_data["checkout"].strftime('%H:%M') if day_data["checkout"] else "-"
                    
                    # Calcular horas
                    hours_str = "-"
                    if day_data["checkin"] and day_data["checkout"]:
                        worked_hours = day_data["checkout"] - day_data["checkin"]
                        hours = worked_hours.total_seconds() / 3600
                        hours_str = f"{int(hours)}:{int((hours % 1) * 60):02d}"
                    
                    items = [formatted_date, checkin_str, checkout_str, hours_str]
                    
                    for col, text in enumerate(items):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.asistencia_table.setItem(row, col, item)
                        
        except Exception as e:
            print(f"Error cargando asistencia personal: {e}")

    def realizar_checkout(self):
        """Checkout al salir de la aplicación"""
        checkout_data = {
            "EmpleadoID": self.usuario_data.get("EmpleadoID"),
            "username": self.usuario_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckOut"
        }
        try:
            response = requests.post('http://localhost:5000/register-evento', json=checkout_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Salida", "Check-Out registrado. ¡Hasta luego!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar checkout: {str(e)}")
            self.close()