from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from firebase_manager import FirebaseManager
from modern_components import ModernLineEdit, ModernButton, AnimatedCard
from register_dialog import RegisterDialog
from core.login_facial import LoginFacial

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.firebase_manager = FirebaseManager()
        self.login_facial = LoginFacial(parent=self)  # Instancia para login facial
        self.setup_ui()
        self.setup_window()
        
    def setup_window(self):
        self.setWindowTitle("Sistema de Gestión - Login")
        self.setFixedSize(600, 700)
        self.center_window()
        
        # Aplicar gradiente de fondo
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667db6, stop:0.5 #0082c8, stop:1 #667db6);
            }
        """)
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(75, 50, 75, 50)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Card principal
        self.login_card = AnimatedCard()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)
        
        # Logo/Título
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.setSpacing(10)
        
        main_title = QLabel("Sistema de Gestión")
        main_title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
        """)
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Inicia sesión para continuar")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(subtitle)
        
        # Campos de entrada
        self.username_edit = ModernLineEdit("Usuario")
        self.username_edit.setFixedHeight(50)
        
        self.password_edit = ModernLineEdit("Contraseña")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setFixedHeight(50)
        self.password_edit.returnPressed.connect(self.login)
        
        # Botones
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        
        self.login_button = ModernButton("Iniciar Sesión", "primary")
        self.login_button.setFixedHeight(50)
        self.login_button.clicked.connect(self.login)
        
        self.register_button = ModernButton("Registrar Empleado", "success")
        self.register_button.setFixedHeight(45)
        self.register_button.clicked.connect(self.show_register)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        
        # Mensaje de estado
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #e74c3c;
                font-weight: 600;
                padding: 10px;
            }
        """)
        
        # Agregar todo al card
        card_layout.addLayout(title_layout)
        card_layout.addWidget(self.username_edit)
        card_layout.addWidget(self.password_edit)
        card_layout.addLayout(button_layout)
        card_layout.addWidget(self.status_label)
        
        self.login_card.setLayout(card_layout)
        main_layout.addWidget(self.login_card)
        
        central_widget.setLayout(main_layout)
    
    def show_message(self, message, color="#e74c3c"):
        """Muestra un mensaje temporal"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {color};
                font-weight: 600;
                padding: 10px;
            }}
        """)
        
        # Timer para limpiar el mensaje
        QTimer.singleShot(4000, lambda: self.status_label.setText(""))
    
    def login(self):
        username = self.username_edit.text().strip().lower()
        password = self.password_edit.text().strip()

        if not username or not password:
            self.show_message("Por favor complete todos los campos")
            return

        if not self.firebase_manager.db:
            self.show_message("Error de conexión con la base de datos")
            return

        # Deshabilitar botón durante la validación
        self.login_button.setEnabled(False)
        self.login_button.setText("Validando...")

        usuario = self.firebase_manager.buscar_usuario(username)

        if usuario and password == usuario.get('password', ''):
            # RECONOCIMIENTO FACIAL OBLIGATORIO
            resultado = self.login_facial.iniciar_login(username)
            if resultado:
                # Solo abre la ventana principal, no muestra mensaje de bienvenida
                self.login_successful.emit(usuario)
                QTimer.singleShot(1500, self.close)
            else:
                self.show_message("Rostro no reconocido. Acceso denegado.")
        elif usuario:
            self.show_message("Contraseña incorrecta")
        else:
            reply = QMessageBox.question(
                self,
                "Usuario no encontrado",
                "El usuario no existe. ¿Desea registrarse?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.show_register()

        # Rehabilitar botón
        self.login_button.setEnabled(True)
        self.login_button.setText("Iniciar Sesión")

    def show_register(self):
        dialog = RegisterDialog(self, self.firebase_manager)
        if dialog.exec():
            self.show_message("Empleado registrado exitosamente. Puede iniciar sesión.", "#27ae60")