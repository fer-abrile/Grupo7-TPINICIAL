from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from datetime import datetime
from modern_components import ModernButton

class MainWindow(QMainWindow):
    def __init__(self, usuario_data, firebase_manager):
        super().__init__()
        self.usuario_data = usuario_data
        self.firebase_manager = firebase_manager

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
        QMessageBox.information(self, "Gráficos", "Aquí se mostrarían los gráficos.")

    def ver_empleados(self):
        QMessageBox.information(self, "Empleados", "Aquí se mostraría la lista de empleados.")

    def realizar_checkout(self):
        # Guardar evento de Checkout en Firebase
        checkout_data = {
            "EmpleadoID": self.usuario_data.get("EmpleadoID"),
            "username": self.usuario_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckOut"
        }
        if hasattr(self.firebase_manager, "registrar_evento"):
            self.firebase_manager.registrar_evento(checkout_data)
        else:
            self.firebase_manager.db.collection("eventos").add(checkout_data)

        QMessageBox.information(self, "Salida", "Se ha registrado el CheckOut correctamente.")
        self.close()