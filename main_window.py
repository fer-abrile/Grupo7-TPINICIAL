from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                             QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent
from datetime import datetime, date
from modern_components import ModernButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from collections import defaultdict

class GraphicsWindow(QMainWindow):
    def __init__(self, firebase_manager, parent=None):
        super().__init__(parent)
        self.firebase_manager = firebase_manager
        self.setWindowTitle("Gráficos de Asistencia")
        self.setFixedSize(900, 600)
        self.setup_ui()
        self.load_data()

        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Gráfico de Check-In/Check-Out del Día")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Crear figura de matplotlib
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Botón cerrar
        close_button = ModernButton("Cerrar", "secondary")
        close_button.clicked.connect(self.close)
        close_button.setFixedSize(100, 40)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        central_widget.setLayout(layout)
        
    def load_data(self):
        try:
            today = date.today().isoformat()
            
            # Obtener datos de Check-In
            checkin_data = []
            if self.firebase_manager.db:
                checkin_docs = self.firebase_manager.db.collection("eventos").where("timestamp", ">=", today).where("timestamp", "<", f"{today}T23:59:59").stream()
                for doc in checkin_docs:
                    data = doc.to_dict()
                    checkin_data.append(data)
            
            # Obtener datos de Check-Out
            checkout_data = []
            if self.firebase_manager.db:
                checkout_docs = self.firebase_manager.db.collection("eventos").where("timestamp", ">=", today).where("timestamp", "<", f"{today}T23:59:59").stream()
                for doc in checkout_docs:
                    data = doc.to_dict()
                    checkout_data.append(data)
            
            self.create_chart(checkin_data, checkout_data)
            
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.create_empty_chart()
    
    def create_chart(self, checkin_data, checkout_data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Contar eventos por hora
        checkin_hours = defaultdict(int)
        checkout_hours = defaultdict(int)
        
        for event in checkin_data:
            try:
                timestamp = datetime.fromisoformat(event['timestamp'])
                hour = timestamp.hour
                checkin_hours[hour] += 1
            except:
                continue
                
        for event in checkout_data:
            try:
                timestamp = datetime.fromisoformat(event['timestamp'])
                hour = timestamp.hour
                checkout_hours[hour] += 1
            except:
                continue
        
        # Preparar datos para el gráfico
        hours = range(24)
        checkin_counts = [checkin_hours[h] for h in hours]
        checkout_counts = [checkout_hours[h] for h in hours]
        
        # Crear gráfico de barras
        x_pos = range(24)
        width = 0.35
        
        bars1 = ax.bar([x - width/2 for x in x_pos], checkin_counts, width, 
                      label='Check-In', color='#27ae60', alpha=0.8)
        bars2 = ax.bar([x + width/2 for x in x_pos], checkout_counts, width,
                      label='Check-Out', color='#e74c3c', alpha=0.8)
        
        # Configurar gráfico
        ax.set_xlabel('Hora del día')
        ax.set_ylabel('Cantidad de eventos')
        ax.set_title(f'Check-In/Check-Out - {date.today().strftime("%d/%m/%Y")}')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([f'{h:02d}:00' for h in hours], rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Añadir valores en las barras
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                       f'{int(height)}', ha='center', va='bottom', fontsize=8)
                       
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                       f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        self.canvas.draw()
    
    def create_empty_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No hay datos para mostrar hoy', 
               ha='center', va='center', transform=ax.transAxes, fontsize=16)
        ax.set_title(f'Check-In/Check-Out - {date.today().strftime("%d/%m/%Y")}')
        self.canvas.draw()


class EmployeeListWindow(QMainWindow):
    def __init__(self, firebase_manager, parent=None):
        super().__init__(parent)
        self.firebase_manager = firebase_manager
        self.setWindowTitle("Lista de Empleados")
        self.setFixedSize(1000, 700)
        self.setup_ui()
        self.load_employees()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Lista de Empleados Registrados")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabla de empleados
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID Empleado", "Nombre", "Apellido", "Área", 
            "Puesto", "Turno", "Fecha Ingreso", "Username"
        ])
        
        # Configurar tabla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Botones
        button_layout = QHBoxLayout()
        
        refresh_button = ModernButton("🔄 Actualizar", "primary")
        refresh_button.clicked.connect(self.load_employees)
        
        close_button = ModernButton("Cerrar", "secondary")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        central_widget.setLayout(layout)
        
    def load_employees(self):
        try:
            if not self.firebase_manager.db:
                QMessageBox.warning(self, "Error", "No hay conexión con la base de datos")
                return
                
            # Obtener todos los empleados
            employees_ref = self.firebase_manager.db.collection("empleados")
            docs = employees_ref.stream()

            employees = []
            for doc in docs:
                data = doc.to_dict()
                employees.append(data)
            
            # Llenar la tabla
            self.table.setRowCount(len(employees))
            
            for row, employee in enumerate(employees):
                self.table.setItem(row, 0, QTableWidgetItem(employee.get("EmpleadoID", "")))
                self.table.setItem(row, 1, QTableWidgetItem(employee.get("Nombre", "")))
                self.table.setItem(row, 2, QTableWidgetItem(employee.get("Apellido", "")))
                self.table.setItem(row, 3, QTableWidgetItem(employee.get("Area", "")))
                self.table.setItem(row, 4, QTableWidgetItem(employee.get("Puesto", "")))
                self.table.setItem(row, 5, QTableWidgetItem(employee.get("Turno", "")))
                self.table.setItem(row, 6, QTableWidgetItem(employee.get("FechaIngreso", "")))
                self.table.setItem(row, 7, QTableWidgetItem(employee.get("username", "")))
            
            # Status
            status_msg = f"Se cargaron {len(employees)} empleados"
            QMessageBox.information(self, "Información", status_msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar empleados: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self, usuario_data, firebase_manager):
        super().__init__()
        self.usuario_data = usuario_data
        self.firebase_manager = firebase_manager
        self.checkout_realizado = False

        self.setWindowTitle("Menú Principal")
        self.setFixedSize(900, 700)
        self.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #667db6, stop:0.5 #0082c8, stop:1 #667db6);
        }
        QWidget#card {
            background-color: white;
            border-radius: 25px;
            padding: 70px;
        }
        QLabel#title {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 40px;
        }

        /* 🎯 SOLO botones dentro del card */
        QWidget#card QPushButton {
            font-size: 18px;
            font-weight: bold;
            padding: 16px;
            border-radius: 12px;
            min-width: 260px;
            color: white;
        }
        QWidget#card QPushButton#graficos {
            background-color: #2980b9;
        }
        QWidget#card QPushButton#graficos:hover {
            background-color: #1f6391;
        }
        QWidget#card QPushButton#empleados {
            background-color: #27ae60;
        }
        QWidget#card QPushButton#empleados:hover {
            background-color: #1e8449;
        }
        QWidget#card QPushButton#salir {
            background-color: #e74c3c;
        }
        QWidget#card QPushButton#salir:hover {
            background-color: #c0392b;
        }
    """)

        # ----------- Layout principal -----------
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ----------- Tarjeta blanca -----------
        card = QWidget()
        card.setObjectName("card")
        card_layout = QVBoxLayout()
        card_layout.setSpacing(35)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Etiqueta de bienvenida
        label = QLabel(f"Bienvenido, {usuario_data['Nombre']} {usuario_data['Apellido']}")
        label.setObjectName("title")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(label)

        # Botones del menú
        self.btn_graficos = ModernButton("📊 Ver Gráficos", "primary")
        
        self.btn_empleados = ModernButton("👥 Ver Empleados", "success")
        
        self.btn_salir = ModernButton("🚪 Salir", "danger")

        # Conexiones
        self.btn_graficos.clicked.connect(self.ver_graficos)
        self.btn_empleados.clicked.connect(self.ver_empleados)
        self.btn_salir.clicked.connect(self.realizar_checkout)

        # Agregar botones al layout
        card_layout.addWidget(self.btn_graficos)
        card_layout.addWidget(self.btn_empleados)
        card_layout.addWidget(self.btn_salir)

        card.setLayout(card_layout)

        # Agregar tarjeta al layout principal
        main_layout.addWidget(card)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # ----------- Funciones de botones -----------
    def ver_graficos(self):
        """Abre ventana de gráficos"""
        self.graphics_window = GraphicsWindow(self.firebase_manager, self)
        self.graphics_window.show()

    def ver_empleados(self):
        """Abre ventana de lista de empleados"""
        self.employee_window = EmployeeListWindow(self.firebase_manager, self)
        self.employee_window.show()

    def closeEvent(self, event: QCloseEvent):
        """Se ejecuta cuando se hace clic en la X de la ventana"""
        # Crear diálogo personalizado
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Salir del Sistema")
        dialog.setText("¿Qué desea hacer?")
        dialog.setInformativeText("Seleccione una opción:")
        
        # Botones personalizados
        btn_checkout_salir = dialog.addButton("Hacer CheckOut y Salir", QMessageBox.ButtonRole.AcceptRole)
        btn_solo_salir = dialog.addButton("Solo Salir", QMessageBox.ButtonRole.DestructiveRole)
        btn_cancelar = dialog.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        
        dialog.setDefaultButton(btn_cancelar)
        dialog.exec()
        
        clicked_button = dialog.clickedButton()
        
        if clicked_button == btn_checkout_salir:
            # Hacer checkout y salir
            self.realizar_checkout_y_salir()
            event.accept()
        elif clicked_button == btn_solo_salir:
            # Solo salir sin checkout
            event.accept()
        else:
            # Cancelar
            event.ignore()

    def realizar_checkout_y_salir(self):
        """Realizar checkout sin mostrar mensaje adicional"""
        checkout_data = {
            "EmpleadoID": self.usuario_data.get("EmpleadoID"),
            "username": self.usuario_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckOut"
        }
        
        try:
            if self.firebase_manager.db:
                self.firebase_manager.db.collection("eventos").add(checkout_data)
                # No mostrar mensaje aquí, solo registrar silenciosamente
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar checkout: {str(e)}")

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