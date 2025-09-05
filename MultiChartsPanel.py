from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from collections import defaultdict
import requests

class MultiChartsPanel(QWidget):
    """Panel para mostrar múltiples gráficos basados en la API Flask"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Análisis de Datos - Múltiples Gráficos")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area para contener gráficos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.charts_layout = QVBoxLayout(container)
        self.charts_layout.setSpacing(30)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Carga datos desde la API Flask y crea los gráficos"""
        try:
            # Datos de MateriaPrima
            materia_prima = []
            r_mat = requests.get('http://localhost:5000/get-materias')
            if r_mat.status_code == 200:
                materia_prima = r_mat.json()
            print("materia prima lista:", materia_prima)

            # Datos de empleados
            employees = []
            r_emp = requests.get('http://localhost:5000/get-empleados')
            if r_emp.status_code == 200:
                employees = r_emp.json()
            print("empleados", employees)

            # Datos de productos
            products = []
            r_prod = requests.get('http://localhost:5000/get-productos')
            if r_prod.status_code == 200:
                products = r_prod.json()
            print("productos", products)

            # Crear gráficos
            self.create_chart_by_product(products)
            self.create_chart_by_material(materia_prima)
            self.create_chart_employees_by_area(employees)
        
        except Exception as e:
            print(f"Error cargando datos para gráficos: {e}")
    
    # ---------------- GRÁFICOS ----------------
    def create_chart_by_product(self, products):
        """Gráfico: Recuento por Producto"""
        counts = defaultdict(int)
        for e in products:
            producto = e.get("id", "Desconocido")
            counts[producto] += 1
        
        self.add_bar_chart(counts, "Recuento por Producto", "Producto", "Cantidad")
    
    def create_chart_by_material(self, materia_prima):
        """Gráfico: Recuento por Materia Prima"""
        counts = defaultdict(int)
        for data in materia_prima:
            materia = data.get("id", "Desconocida")
            counts[materia] += 1

        self.add_bar_chart(counts, "Recuento por Materia Prima", "Materia Prima", "Cantidad")

    def create_chart_employees_by_area(self, employees):
        """Gráfico: Cantidad de empleados por área"""
        counts = defaultdict(int)
        for data in employees:
            area = data.get("Area", "Sin Área")
            counts[area] += 1

        self.add_bar_chart(counts, "Empleados por Área", "Área", "Cantidad")
    
    # ---------------- MÉTODO AUXILIAR ----------------
    def add_bar_chart(self, data_dict, title, xlabel, ylabel):
        """Crea un gráfico de barras y lo agrega al layout"""
        figure = Figure(figsize=(10, 5))
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        
        keys = list(data_dict.keys())
        values = list(data_dict.values())
        x_pos = range(len(keys))
        
        bars = ax.bar(x_pos, values, color='#3498db', alpha=0.8)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(keys, rotation=45, ha='right')
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(axis='y', alpha=0.3)
        
        # Valores encima de barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        canvas.setFixedHeight(400)
        
        self.charts_layout.addWidget(canvas)
