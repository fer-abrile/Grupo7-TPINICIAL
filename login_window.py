from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QMessageBox, QApplication, QDialog, QPushButton)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from firebase_manager import FirebaseManager
from modern_components import ModernLineEdit, ModernButton, AnimatedCard
from register_dialog import RegisterDialog, CameraPopup
from datetime import datetime
import face_recognition
import numpy as np

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.firebase_manager = FirebaseManager()
        self.setup_ui()
        self.setup_window()
        
    def setup_window(self):
        self.setWindowTitle("Sistema de Gestión - Login")
        self.setFixedSize(600, 700)
        self.center_window()
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667db6, stop:0.5 #0082c8, stop:1 #667db6);
            }
        """)
    
    def center_window(self):
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
        
        self.login_card = AnimatedCard()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)
        
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
        
        self.username_edit = ModernLineEdit("Usuario")
        self.username_edit.setFixedHeight(50)
        
        self.password_edit = ModernLineEdit("Contraseña")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setFixedHeight(50)
        self.password_edit.returnPressed.connect(self.login)
        
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
        
        card_layout.addLayout(title_layout)
        card_layout.addWidget(self.username_edit)
        card_layout.addWidget(self.password_edit)
        card_layout.addLayout(button_layout)
        card_layout.addWidget(self.status_label)
        
        self.login_card.setLayout(card_layout)
        main_layout.addWidget(self.login_card)
        
        central_widget.setLayout(main_layout)
    
    def show_message(self, message, color="#e74c3c"):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {color};
                font-weight: 600;
                padding: 10px;
            }}
        """)
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
        
        self.login_button.setEnabled(False)
        self.login_button.setText("Validando...")
        
        usuario = self.firebase_manager.buscar_usuario(username)
        
        if usuario:
            if password == usuario.get('password', ''):
                # Validar rostro
                if 'face_embedding' not in usuario or not usuario['face_embedding']:
                    self.show_message("El usuario no tiene rostro registrado.")
                    self.login_button.setEnabled(True)
                    self.login_button.setText("Iniciar Sesión")
                    return

                # Abrir pop-up de cámara para validar rostro
                popup = CameraPopup(self)
                if popup.exec():
                    captured_embedding = popup.face_embedding
                    if captured_embedding is None:
                        self.show_message("No se pudo capturar el rostro.")
                        self.login_button.setEnabled(True)
                        self.login_button.setText("Iniciar Sesión")
                        return
                    # Comparar embeddings
                    known_embedding = np.array(usuario['face_embedding'])
                    matches = face_recognition.compare_faces([known_embedding], np.array(captured_embedding), tolerance=0.5)
                    if matches[0]:
                        self.show_message(f"¡Bienvenido {usuario['Nombre']} {usuario['Apellido']}!", "#27ae60")
                        self.registrar_checkin(usuario)
                        self.login_successful.emit(usuario)
                        QTimer.singleShot(1500, self.close)
                    else:
                        self.show_message("El rostro no coincide con el usuario.")
                else:
                    self.show_message("Validación de rostro cancelada.")
            else:
                self.show_message("Contraseña incorrecta")
        else:
            reply = QMessageBox.question(self, "Usuario no encontrado", 
                                       "El usuario no existe. ¿Desea registrarse?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.show_register()
        
        self.login_button.setEnabled(True)
        self.login_button.setText("Iniciar Sesión")
    
    def registrar_checkin(self, usuario):
        if not self.firebase_manager.db:
            return
        checkin_data = {
            "EmpleadoID": usuario.get("EmpleadoID"),
            "username": usuario.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckIn"
        }
        # Suponiendo que tienes un método para guardar eventos en Firebase
        if hasattr(self.firebase_manager, "registrar_evento"):
            self.firebase_manager.registrar_evento(checkin_data)
        else:
            # Alternativamente, puedes guardar en una colección "CheckIn"
            self.firebase_manager.db.collection("CheckIn").add(checkin_data)
    
    def show_register(self):
        dialog = RegisterDialog(self, self.firebase_manager)
        if dialog.exec():
            self.show_message("Empleado registrado exitosamente. Puede iniciar sesión.", "#27ae60")