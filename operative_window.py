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
                    stop:0 #2c3e50, stop:1 #34495e);
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
        self.production_panel = ProductionControlPanel(self.usuario_data)
        self.inventory_panel = InventoryPanel(self.usuario_data)  
        self.incident_panel = IncidentReportPanel(self.usuario_data)
        self.my_attendance_panel = MyAttendancePanel(self.usuario_data)

        self.content_area.addWidget(self.welcome_panel)        # 0
        self.content_area.addWidget(self.production_panel)     # 1
        self.content_area.addWidget(self.inventory_panel)      # 2
        self.content_area.addWidget(self.incident_panel)       # 3
        self.content_area.addWidget(self.my_attendance_panel)  # 4

        self.inventory_panel.production_panel = self.production_panel

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
# PANELES ESPECÍFICOS PARA OPERARIOS
# -----------------------------

class ProductionControlPanel(QWidget):
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        # Datos locales para producción (no se guardan en API)
        self.local_production_data = []
        self.setup_ui()
        self.update_local_kpis()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Control de Producción")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Sección de métricas rápidas
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        self.produccion_card = self.create_metric_card("Producción Hoy", "0", "#3498db")
        self.eficiencia_card = self.create_metric_card("Eficiencia", "0%", "#27ae60") 
        self.defectos_card = self.create_metric_card("Desperdicio", "0", "#e74c3c")

        metrics_layout.addWidget(self.produccion_card)
        metrics_layout.addWidget(self.eficiencia_card)
        metrics_layout.addWidget(self.defectos_card)
        
        layout.addLayout(metrics_layout)

        # Formulario para registrar producción
        form_layout = QVBoxLayout()
        form_section = QLabel("Registrar Producción")
        form_section.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        form_layout.addWidget(form_section)

        form_inputs = QFormLayout()
        self.producto_combo = QComboBox()
        self.producto_combo.addItems(["Harina", "Fideos", "Azúcar", "Arroz"])
        
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setRange(1, 9999)
        self.cantidad_spin.setValue(1)
        
        self.turno_combo = QComboBox()
        self.turno_combo.addItems(["Mañana", "Tarde", "Noche"])
        
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
        self.btn_registrar.clicked.connect(self.registrar_produccion_local)

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

    def create_metric_card(self, title, value, color):
        """Crear tarjeta de métrica"""
        card_container = QWidget()
        card_container.setFixedHeight(120)
        
        main_layout = QVBoxLayout(card_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        inner_card = QWidget()
        inner_card.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 12px;
                border: 2px solid rgba(255, 255, 255, 0.2);
            }}
        """)
        
        content_layout = QVBoxLayout(inner_card)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: white; 
                font-size: 14px; 
                font-weight: bold;
                text-align: center;
                margin-bottom: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet("""
            QLabel {
                color: white; 
                font-size: 24px; 
                font-weight: bold;
                text-align: center;
                margin-top: 5px;
            }
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(value_label)
        
        main_layout.addWidget(inner_card)
        
        card_container.title_label = title_label
        card_container.value_label = value_label
        card_container.inner_card = inner_card
        
        return card_container

    def registrar_produccion_local(self):
        """Registrar producción solo localmente (no guarda en API)"""
        try:
            producto_nombre = self.producto_combo.currentText()
            cantidad = self.cantidad_spin.value()
            
            # Crear registro local
            production_record = {
                "producto": producto_nombre,
                "cantidad": cantidad,
                "turno": self.turno_combo.currentText(),
                "timestamp": datetime.now().isoformat(),
                "operario": f"{self.usuario_data.get('Nombre', '')} {self.usuario_data.get('Apellido', '')}"
            }
            
            # Agregar a datos locales
            self.local_production_data.append(production_record)
            
            # Actualizar interfaz
            self.load_local_production_data()
            self.update_local_kpis()
            
            # Limpiar formulario
            self.cantidad_spin.setValue(1)
            
            QMessageBox.information(self, "Éxito", "Producción registrada localmente.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error registrando producción: {str(e)}")

    def load_local_production_data(self):
        """Cargar datos locales de producción del día"""
        try:
            today = date.today().isoformat()
            produccion_hoy = [p for p in self.local_production_data 
                             if p.get('timestamp', '').startswith(today)]
            
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
            print(f"Error cargando producción local: {e}")

    def update_local_kpis(self):
        """Actualizar KPIs basados en datos locales"""
        try:
            today = date.today().isoformat()
            
            # Contar producción de hoy
            produccion_hoy = sum(p.get('cantidad', 0) for p in self.local_production_data 
                               if p.get('timestamp', '').startswith(today))
            
            # Buscar desperdicios si hay referencia al panel de inventario
            desperdicios_hoy = 0
            try:
                if hasattr(self, 'parent') and hasattr(self.parent(), 'inventory_panel'):
                    inventory_panel = self.parent().inventory_panel
                    if hasattr(inventory_panel, 'local_desperdicio_data'):
                        desperdicios_hoy = sum(d.get('cantidad', 0) 
                                             for d in inventory_panel.local_desperdicio_data 
                                             if d.get('timestamp', '').startswith(today))
            except:
                pass
            
            # Calcular eficiencia (basada en meta de 100 items por día)
            meta_diaria = 100
            eficiencia = min(100, (produccion_hoy / meta_diaria) * 100) if meta_diaria > 0 else 0
            
            # Actualizar tarjetas
            if hasattr(self.produccion_card, 'value_label'):
                self.produccion_card.value_label.setText(str(produccion_hoy))
            
            if hasattr(self.eficiencia_card, 'value_label'):
                self.eficiencia_card.value_label.setText(f"{eficiencia:.1f}%")
                
            if hasattr(self.defectos_card, 'value_label'):
                self.defectos_card.value_label.setText(str(desperdicios_hoy))
            
            # Forzar actualización visual
            self.produccion_card.repaint()
            self.eficiencia_card.repaint()
            self.defectos_card.repaint()
            
        except Exception as e:
            print(f"Error actualizando KPIs locales: {e}")

    def update_desperdicio_count(self, cantidad):
        """Actualiza el contador de desperdicios desde el panel de inventario"""
        try:
            current_value = int(self.defectos_card.value_label.text())
            new_value = current_value + cantidad
            self.defectos_card.value_label.setText(str(new_value))
            self.defectos_card.repaint()
        except Exception as e:
            print(f"Error actualizando contador de desperdicios: {e}")
    
class InventoryPanel(QWidget):
    def __init__(self, usuario_data=None, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data or {}
        # Datos locales para desperdicio (no se guardan en API)
        self.local_desperdicio_data = []
        self.cached_products = []
        self.setup_ui()
        self.load_inventory_from_api()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        title = QLabel("Gestión de Inventario")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Formulario para registrar desperdicio
        desperdicio_section = QLabel("Registrar Desperdicio")
        desperdicio_section.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(desperdicio_section)

        desperdicio_layout = QFormLayout()
        
        self.desperdicio_producto_combo = QComboBox()
        self.desperdicio_producto_combo.addItems(["Producto A", "Producto B", "Producto C", "Producto D"])
        
        self.desperdicio_cantidad_spin = QSpinBox()
        self.desperdicio_cantidad_spin.setRange(1, 9999)
        self.desperdicio_cantidad_spin.setValue(1)
        
        self.motivo_combo = QComboBox()
        self.motivo_combo.addItems([
            "Material Defectuoso", "Error de Proceso", "Daño en Transporte",
            "Caducidad", "Falla de Equipo", "Error Humano", "Otro"
        ])
        
        self.descripcion_desperdicio = QLineEdit()
        self.descripcion_desperdicio.setPlaceholderText("Descripción opcional del motivo...")
        
        # Estilos para formulario de desperdicio
        form_style = """
            QComboBox, QSpinBox, QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
                border-color: #e74c3c;
            }
        """
        self.desperdicio_producto_combo.setStyleSheet(form_style)
        self.desperdicio_cantidad_spin.setStyleSheet(form_style)
        self.motivo_combo.setStyleSheet(form_style)
        self.descripcion_desperdicio.setStyleSheet(form_style)

        desperdicio_layout.addRow("Producto:", self.desperdicio_producto_combo)
        desperdicio_layout.addRow("Cantidad:", self.desperdicio_cantidad_spin)
        desperdicio_layout.addRow("Motivo:", self.motivo_combo)
        desperdicio_layout.addRow("Descripción:", self.descripcion_desperdicio)

        self.btn_registrar_desperdicio = ModernButton("Registrar Desperdicio", "danger")
        self.btn_registrar_desperdicio.clicked.connect(self.registrar_desperdicio_local)

        layout.addLayout(desperdicio_layout)
        layout.addWidget(self.btn_registrar_desperdicio)

        # Tabla de desperdicios registrados
        desperdicio_table_title = QLabel("Desperdicios Registrados Hoy")
        desperdicio_table_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(desperdicio_table_title)

        self.desperdicio_table = QTableWidget()
        self.desperdicio_table.setColumnCount(5)
        self.desperdicio_table.setHorizontalHeaderLabels([
            "Hora", "Producto", "Cantidad", "Motivo", "Operario"
        ])
        header = self.desperdicio_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.desperdicio_table.setMaximumHeight(200)
        
        layout.addWidget(self.desperdicio_table)

        # Separador visual
        separator = QLabel()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #bdc3c7; margin: 20px 0;")
        layout.addWidget(separator)

        # Tabla de inventario
        inventory_title = QLabel("Estado del Inventario")
        inventory_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px 0;")
        layout.addWidget(inventory_title)

        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID Producto", "Nombre", "Stock Actual", "Stock Mínimo", "Estado"
        ])
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.inventory_table)

        # Botón actualizar inventario
        btn_layout = QHBoxLayout()
        self.btn_actualizar = ModernButton("Actualizar Inventario", "primary")
        self.btn_actualizar.clicked.connect(self.load_inventory_from_api)
        
        btn_layout.addWidget(self.btn_actualizar)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def registrar_desperdicio_local(self):
        """Registrar desperdicio solo localmente (no guarda en API)"""
        try:
            producto_nombre = self.desperdicio_producto_combo.currentText()
            cantidad = self.desperdicio_cantidad_spin.value()
            
            if not producto_nombre.strip():
                QMessageBox.warning(self, "Error", "Seleccione un producto válido.")
                return
            
            if cantidad <= 0:
                QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a 0.")
                return
            
            # Crear registro local
            desperdicio_record = {
                'producto': producto_nombre,
                'cantidad': cantidad,
                'motivo': self.motivo_combo.currentText(),
                'descripcion': self.descripcion_desperdicio.text().strip(),
                'timestamp': datetime.now().isoformat(),
                'operario': f"{self.usuario_data.get('Nombre', '')} {self.usuario_data.get('Apellido', '')}",
                'tipo': 'desperdicio'
            }
            
            # Agregar a datos locales
            self.local_desperdicio_data.append(desperdicio_record)
            
            # Limpiar formulario
            self.desperdicio_cantidad_spin.setValue(1)
            self.descripcion_desperdicio.clear()
            
            # Actualizar tabla local
            self.load_local_desperdicio_data()
            
            # Actualizar KPIs del panel de producción si existe
            try:
                if hasattr(self, 'production_panel') and self.production_panel:
                    self.production_panel.update_local_kpis()
            except:
                pass
            
            QMessageBox.information(self, "Éxito", f"Desperdicio registrado localmente.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar desperdicio: {str(e)}")

    def load_local_desperdicio_data(self):
        """Cargar datos locales de desperdicios del día"""
        try:
            today = date.today().isoformat()
            desperdicios_hoy = [d for d in self.local_desperdicio_data 
                              if d.get('timestamp', '').startswith(today)]
            
            self.desperdicio_table.setRowCount(len(desperdicios_hoy))
            for row, desp in enumerate(desperdicios_hoy):
                try:
                    timestamp = datetime.fromisoformat(desp.get('timestamp', ''))
                    formatted_time = timestamp.strftime('%H:%M')
                except:
                    formatted_time = "N/A"
                
                items = [
                    formatted_time,
                    desp.get("producto", "N/A"),
                    str(desp.get("cantidad", 0)),
                    desp.get("motivo", "N/A"),
                    desp.get("operario", "N/A")
                ]
                
                for col, text in enumerate(items):
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.desperdicio_table.setItem(row, col, item)
                    
        except Exception as e:
            print(f"Error cargando desperdicios locales: {e}")

    def load_inventory_from_api(self):
        """Cargar inventario desde la API (único GET para inventario)"""
        try:
            response = requests.get('http://localhost:5000/get-productos')
            if response.status_code == 200:
                products = response.json()
                self.cached_products = products
                
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
        # Datos locales para incidencias (no se guardan en API)
        self.local_incident_data = []
        self.setup_ui()
        self.load_local_incident_data()

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
        self.btn_enviar.clicked.connect(self.enviar_reporte_local)
        layout.addWidget(self.btn_enviar)
        
        # Historial de reportes
        history_title = QLabel("Mis Reportes")
        history_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(history_title)
        
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(5)
        self.reports_table.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Prioridad", "Estado", "Descripción"
        ])
        header = self.reports_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.reports_table)
        
        self.setLayout(layout)

    def enviar_reporte_local(self):
        """Enviar reporte de incidencia solo localmente (no guarda en API)"""
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
            
            # Agregar a datos locales
            self.local_incident_data.append(report_data)
            
            # Limpiar formulario
            self.descripcion_text.clear()
            
            # Actualizar tabla
            self.load_local_incident_data()
            
            QMessageBox.information(self, "Éxito", "Incidencia reportada localmente.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error enviando reporte: {str(e)}")

    def load_local_incident_data(self):
        """Cargar reportes locales del usuario actual"""
        try:
            # Filtrar reportes del usuario actual
            empleado_id = self.usuario_data.get("EmpleadoID")
            user_reports = [r for r in self.local_incident_data if r.get("empleado_id") == empleado_id]
            user_reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            self.reports_table.setRowCount(len(user_reports))
            for row, report in enumerate(user_reports):
                try:
                    timestamp = datetime.fromisoformat(report.get('timestamp', ''))
                    formatted_date = timestamp.strftime('%d/%m/%Y %H:%M')
                except:
                    formatted_date = "N/A"
                
                descripcion = report.get("descripcion", "")
                if len(descripcion) > 50:
                    descripcion = descripcion[:50] + "..."
                
                items = [
                    formatted_date,
                    report.get("tipo", "N/A"),
                    report.get("prioridad", "N/A"),
                    report.get("estado", "Pendiente"),
                    descripcion
                ]
                
                for col, text in enumerate(items):
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Colorear según prioridad
                    if col == 2:  # Columna prioridad
                        if "Crítica" in text:
                            item.setBackground(Qt.GlobalColor.red)
                            item.setForeground(Qt.GlobalColor.white)
                        elif "Alta" in text:
                            item.setBackground(Qt.GlobalColor.yellow)
                    
                    self.reports_table.setItem(row, col, item)
                    
        except Exception as e:
            print(f"Error cargando reportes locales: {e}")

class MyAttendancePanel(QWidget):
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.cached_events = []
        self.setup_ui()
        self.load_attendance_from_api()

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
        self.checkins_card = self.create_summary_card("Check-Ins", "0", "#3498db")
        self.checkouts_card = self.create_summary_card("Check-Outs", "0", "#e74c3c")
        self.horas_card = self.create_summary_card("Total Horas", "0:00", "#27ae60")
        
        summary_layout.addWidget(self.checkins_card)
        summary_layout.addWidget(self.checkouts_card)
        summary_layout.addWidget(self.horas_card)
        
        layout.addLayout(summary_layout)

        # Botón actualizar
        btn_layout = QHBoxLayout()
        self.btn_actualizar_asistencia = ModernButton("Actualizar Asistencia", "info")
        self.btn_actualizar_asistencia.clicked.connect(self.load_attendance_from_api)
        btn_layout.addWidget(self.btn_actualizar_asistencia)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Tabla de eventos de hoy
        today_events_title = QLabel("Eventos de Hoy")
        today_events_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(today_events_title)

        self.today_events_table = QTableWidget()
        self.today_events_table.setColumnCount(4)
        self.today_events_table.setHorizontalHeaderLabels([
            "Hora", "Tipo", "Duración Desde Anterior", "Acumulado"
        ])
        header = self.today_events_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.today_events_table.setMaximumHeight(300)
        
        layout.addWidget(self.today_events_table)

        # Historial de asistencia
        history_title = QLabel("Historial de Asistencia (Últimos 7 días)")
        history_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(history_title)

        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(4)
        self.attendance_table.setHorizontalHeaderLabels([
            "Fecha", "Check-Ins", "Check-Outs", "Total Horas"
        ])
        header = self.attendance_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.attendance_table)
        self.setLayout(layout)

    def create_summary_card(self, title, value, color):
        """Crear tarjeta de resumen"""
        card = QWidget()
        card.setFixedHeight(80)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 10px;
                padding: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Guardar referencia al value_label para poder actualizarlo
        card.value_label = value_label
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card

    def calculate_time_difference(self, time1, time2):
        """Calcular diferencia entre dos timestamps y devolver en formato legible"""
        try:
            if isinstance(time1, str):
                time1 = datetime.fromisoformat(time1)
            if isinstance(time2, str):
                time2 = datetime.fromisoformat(time2)
            
            diff = abs(time2 - time1)
            total_seconds = diff.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "N/A"

    def calculate_total_work_time(self, eventos_del_dia):
        """Calcular tiempo total trabajado basado en pares CheckIn-CheckOut"""
        try:
            checkins = []
            checkouts = []
            
            for evento in eventos_del_dia:
                timestamp_str = evento.get('timestamp', '')
                if not timestamp_str:
                    continue
                    
                timestamp = datetime.fromisoformat(timestamp_str)
                evento_tipo = evento.get("evento")
                
                if evento_tipo == "CheckIn":
                    checkins.append(timestamp)
                elif evento_tipo == "CheckOut":
                    checkouts.append(timestamp)
            
            checkins.sort()
            checkouts.sort()
            
            total_seconds = 0
            i = 0
            
            for checkin in checkins:
                checkout_found = None
                for j in range(i, len(checkouts)):
                    if checkouts[j] > checkin:
                        checkout_found = checkouts[j]
                        i = j + 1
                        break
                
                if checkout_found:
                    work_session = checkout_found - checkin
                    if work_session.total_seconds() > 0:
                        total_seconds += work_session.total_seconds()
            
            total_hours = total_seconds / 3600
            hours = int(total_hours)
            minutes = int((total_hours % 1) * 60)
            
            return f"{hours}:{minutes:02d}"
            
        except Exception as e:
            print(f"Error calculando tiempo total: {e}")
            return "0:00"

    def load_attendance_from_api(self):
        """Cargar asistencia desde la API (único GET para asistencia)"""
        try:
            empleado_id = self.usuario_data.get("EmpleadoID")
            print(f"Cargando asistencia para empleado ID: {empleado_id}")
            
            response = requests.get('http://localhost:5000/get-eventos')
            if response.status_code == 200:
                eventos = response.json()
                self.cached_events = eventos
                
                # Filtrar eventos del usuario actual
                my_eventos = [e for e in eventos if e.get("EmpleadoID") == empleado_id]
                
                # Agrupar eventos por día
                eventos_por_dia = defaultdict(list)
                end_date = date.today()
                start_date = end_date - timedelta(days=7)
                
                for evento in my_eventos:
                    try:
                        timestamp_str = evento.get('timestamp', '')
                        if not timestamp_str:
                            continue
                            
                        timestamp = datetime.fromisoformat(timestamp_str)
                        day_key = timestamp.date().isoformat()
                        
                        if start_date <= timestamp.date() <= end_date:
                            eventos_por_dia[day_key].append(evento)
                            
                    except Exception as e:
                        print(f"Error procesando evento: {e}")
                        continue
                
                # Procesar eventos de hoy
                today_key = date.today().isoformat()
                if today_key in eventos_por_dia:
                    self.load_today_events(eventos_por_dia[today_key])
                
                # Llenar tabla de historial
                self.load_history_table(eventos_por_dia)
                
                QMessageBox.information(self, "Actualizado", "Asistencia actualizada desde el servidor.")
                        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando asistencia: {str(e)}")

    def load_today_events(self, eventos_hoy):
        """Cargar y mostrar todos los eventos de hoy"""
        try:
            eventos_ordenados = sorted(eventos_hoy, 
                key=lambda x: datetime.fromisoformat(x.get('timestamp', '1900-01-01T00:00:00')))
            
            # Contar check-ins y check-outs
            checkins_count = sum(1 for e in eventos_ordenados if e.get("evento") == "CheckIn")
            checkouts_count = sum(1 for e in eventos_ordenados if e.get("evento") == "CheckOut")
            
            # Actualizar tarjetas de resumen
            self.checkins_card.value_label.setText(str(checkins_count))
            self.checkouts_card.value_label.setText(str(checkouts_count))
            
            # Calcular tiempo total trabajado
            total_time = self.calculate_total_work_time(eventos_ordenados)
            self.horas_card.value_label.setText(total_time)
            
            # Llenar tabla de eventos de hoy
            self.today_events_table.setRowCount(len(eventos_ordenados))
            
            tiempo_acumulado = 0
            evento_anterior = None
            
            for row, evento in enumerate(eventos_ordenados):
                try:
                    timestamp = datetime.fromisoformat(evento.get('timestamp', ''))
                    hora = timestamp.strftime('%H:%M:%S')
                    tipo = evento.get("evento")
                    
                    # Calcular duración desde evento anterior
                    duracion_str = "-"
                    if evento_anterior:
                        duracion_str = self.calculate_time_difference(
                            evento_anterior.get('timestamp'), 
                            evento.get('timestamp')
                        )
                    
                    # Calcular tiempo acumulado
                    acumulado_str = "-"
                    if tipo == "CheckOut" and evento_anterior and evento_anterior.get("evento") == "CheckIn":
                        try:
                            checkin_time = datetime.fromisoformat(evento_anterior.get('timestamp'))
                            checkout_time = timestamp
                            session_time = (checkout_time - checkin_time).total_seconds()
                            if session_time > 0:
                                tiempo_acumulado += session_time
                                hours = int(tiempo_acumulado // 3600)
                                minutes = int((tiempo_acumulado % 3600) // 60)
                                acumulado_str = f"{hours}:{minutes:02d}"
                        except:
                            pass
                    
                    items = [hora, tipo, duracion_str, acumulado_str]
                    
                    for col, text in enumerate(items):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        
                        # Colorear según el tipo
                        if col == 1:  # Columna tipo
                            if "CheckIn" in text:
                                item.setBackground(Qt.GlobalColor.green)
                                item.setForeground(Qt.GlobalColor.white)
                            elif "CheckOut" in text:
                                item.setBackground(Qt.GlobalColor.red)
                                item.setForeground(Qt.GlobalColor.white)
                        
                        self.today_events_table.setItem(row, col, item)
                    
                    evento_anterior = evento
                    
                except Exception as e:
                    print(f"Error procesando evento en fila {row}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error cargando eventos de hoy: {e}")

    def load_history_table(self, eventos_por_dia):
        """Cargar tabla de historial con resumen por día"""
        try:
            sorted_days = sorted(eventos_por_dia.keys(), reverse=True)
            self.attendance_table.setRowCount(len(sorted_days))
            
            for row, day_key in enumerate(sorted_days):
                eventos_del_dia = eventos_por_dia[day_key]
                
                # Formatear fecha
                try:
                    day_date = datetime.fromisoformat(day_key).strftime('%d/%m/%Y')
                except:
                    day_date = day_key
                
                # Contar eventos
                checkins = sum(1 for e in eventos_del_dia if e.get("evento") == "CheckIn")
                checkouts = sum(1 for e in eventos_del_dia if e.get("evento") == "CheckOut")
                
                # Calcular tiempo total
                total_time = self.calculate_total_work_time(eventos_del_dia)
                
                items = [day_date, f"{checkins}", f"{checkouts}", total_time]
                
                for col, text in enumerate(items):
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Resaltar el día actual
                    if day_key == date.today().isoformat():
                        item.setBackground(Qt.GlobalColor.lightGray)
                    
                    self.attendance_table.setItem(row, col, item)
                    
        except Exception as e:
            print(f"Error cargando tabla de historial: {e}")