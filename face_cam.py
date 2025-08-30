from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self, usuario_data):
        super().__init__()
        self.setWindowTitle("Opciones del Usuario")
        self.setFixedSize(800, 600)
        central_widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(f"Bienvenido, {usuario_data['Nombre']} {usuario_data['Apellido']}")
        layout.addWidget(label)
        # Aquí puedes agregar botones u opciones vacías
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)