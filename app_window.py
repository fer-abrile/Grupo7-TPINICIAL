from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QInputDialog, QMessageBox

from core.registro_datos import RegistroDatos
from core.graficos import Graficos
from core.login_facial import LoginFacial


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("App Reconocimiento Facial")
        self.setGeometry(100, 100, 400, 300)

        # Instancias de lógica
        self.registro = RegistroDatos()
        self.graficos = Graficos(path_csvs="data/")
        self.login = LoginFacial(parent=self)   # le paso el parent para usar QMessageBox

        # Layout principal
        layout = QVBoxLayout()

        # Título
        label = QLabel("Menú Principal")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

        # Botones
        btn_registro = QPushButton("Registrarse")
        btn_registro.clicked.connect(self.registrar)
        layout.addWidget(btn_registro)

        btn_login = QPushButton("Iniciar Sesión")
        btn_login.clicked.connect(self.login.iniciar_login)  # delega la lógica a LoginFacial
        layout.addWidget(btn_login)

        btn_graficos = QPushButton("Mostrar Gráficos")
        btn_graficos.clicked.connect(self.graficos.menu_graficos)
        layout.addWidget(btn_graficos)

        btn_salir = QPushButton("Salir")
        btn_salir.clicked.connect(self.close)
        layout.addWidget(btn_salir)

        self.setLayout(layout)

    # -----------------------------
    # MÉTODOS DE BOTONES
    # -----------------------------
    def registrar(self):
        nombre, ok = QInputDialog.getText(self, "Registro", "Ingresa tu nombre:")
        if ok and nombre:
            self.registro.registrar_usuario(nombre)
            QMessageBox.information(self, "Registro", f"Usuario {nombre} registrado con éxito.")
