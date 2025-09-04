# main_window.py

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
    def __init__(self, firebase_manager, parent=None):
        super().__init__(parent)
        self.firebase_manager = firebase_manager
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
            checkin_data = []
            checkout_data = []

            if self.firebase_manager.db:
                docs = self.firebase_manager.db.collection("eventos")\
                    .where("timestamp", ">=", today)\
                    .where("timestamp", "<", f"{today}T23:59:59").stream()
                for doc in docs:
                    data = doc.to_dict()
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
    def __init__(self, firebase_manager, parent=None):
        super().__init__(parent)
        self.firebase_manager = firebase_manager
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
        if not self.firebase_manager.db: return
        docs = self.firebase_manager.db.collection("empleados").stream()
        empleados = [doc.to_dict() for doc in docs]

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

# -----------------------------
# PANEL MULTI-GRAFICOS
# -----------------------------
class MultiChartsPanel(QWidget):
    """Panel con los 3 gráficos extra: por producto, materia prima y empleados por área"""
    def __init__(self, firebase_manager, parent=None):
        super().__init__(parent)
        self.firebase_manager = firebase_manager
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
            if not self.firebase_manager.db: return
            self.figure.clear()
            ax1 = self.figure.add_subplot(311)
            ax2 = self.figure.add_subplot(312)
            ax3 = self.figure.add_subplot(313)

            # Datos de productos
            productos_count = defaultdict(int)
            materias_count = defaultdict(int)
            area_count = defaultdict(int)

            
            docs_productos = self.firebase_manager.db.collection("Productos").stream()
            docs_materias = self.firebase_manager.db.collection("MateriaPrima").stream()
            docs_empleados = self.firebase_manager.db.collection("Empleados").stream()
            
            for doc in docs_productos:
                data = doc.to_dict()
                producto_id = data.get("id")
                stock_actual = data.get("stock_actual")

                if producto_id is not None and stock_actual is not None:
                    productos_count[producto_id] = stock_actual
            for doc in docs_empleados:
                data = doc.to_dict()
                area = data.get("Area")
                if area: area_count[area] +=1
            for doc in docs_materias:
                data = doc.to_dict()
                materia = data.get("id")
                if materia: materias_count[materia] +=1

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
    def __init__(self, usuario_data, firebase_manager):
        super().__init__()
        self.usuario_data = usuario_data
        self.firebase_manager = firebase_manager
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
        self.graphics_panel = GraphicsPanel(self.firebase_manager)
        self.employee_panel = EmployeePanel(self.firebase_manager)
        self.multi_charts_panel = MultiChartsPanel(self.firebase_manager)

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
                if self.firebase_manager.db:
                    self.firebase_manager.db.collection("eventos").add(checkout_data)
                    QMessageBox.information(self, "Salida", "Se ha registrado el CheckOut correctamente.")
                    self.close()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al registrar checkout: {str(e)}")
