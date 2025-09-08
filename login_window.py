from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QMessageBox, QApplication, QDialog, QPushButton)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from modern_components import ModernLineEdit, ModernButton, AnimatedCard
from register_dialog import RegisterDialog
from datetime import datetime
from main_window import MainWindow
import face_recognition
import numpy as np
import cv2
import requests

class FacialVerificationDialog(QDialog):
    def __init__(self, parent=None, known_embedding=None, username=""):
        super().__init__(parent)
        self.known_embedding = known_embedding
        self.username = username
        self.setWindowTitle(f"Verificación Facial - {username}")
        self.setModal(True)
        self.setFixedSize(640, 550)
        self.verification_successful = False
        
        # Variables para el procesamiento
        self.cap = None
        self.timer = None
        self.current_frame = None
        
        self.setup_ui()
        self.start_camera()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title = QLabel(f"Verificando identidad de: {self.username}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
                padding: 10px;
                background-color: rgba(52, 152, 219, 0.1);
                border-radius: 8px;
            }
        """)
        layout.addWidget(title)
        
        # Video feed
        self.video_label = QLabel()
        self.video_label.setFixedSize(600, 450)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 3px solid #3498db;
                border-radius: 10px;
                background-color: #ecf0f1;
            }
        """)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status label
        self.status_label = QLabel("Posicione su rostro frente a la cámara...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding: 8px;
                font-weight: 500;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Botones
        button_layout = QHBoxLayout()
        self.cancel_button = ModernButton("Cancelar", "danger")
        self.cancel_button.clicked.connect(self.cancel_verification)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "No se puede acceder a la cámara")
            self.reject()
            return
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms = ~33 FPS
        
    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
            
        self.current_frame = frame.copy()
        
        # Procesar reconocimiento facial
        self.process_facial_recognition(frame)
        
        # Convertir frame para mostrar en Qt
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # Escalar manteniendo aspecto
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)
        
    def process_facial_recognition(self, frame):
        # Reducir resolución para procesar más rápido
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detectar caras
        face_locations = face_recognition.face_locations(rgb_small_frame)
        
        if not face_locations:
            self.status_label.setText("No se detecta rostro. Posiciónese frente a la cámara.")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #f39c12;
                    padding: 8px;
                    font-weight: 500;
                }
            """)
            return
            
        if len(face_locations) > 1:
            self.status_label.setText("Múltiples rostros detectados. Solo debe haber una persona.")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #e74c3c;
                    padding: 8px;
                    font-weight: 500;
                }
            """)
            # Dibujar rectángulos rojos para múltiples caras
            for face_location in face_locations:
                top, right, bottom, left = face_location
                top *= 4; right *= 4; bottom *= 4; left *= 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 3)
                cv2.putText(frame, "MULTIPLE FACES", (left, top - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            return
        
        # Una sola cara detectada - procesar
        face_location = face_locations[0]
        top, right, bottom, left = face_location
        
        # Obtener encoding de la cara detectada
        face_encodings = face_recognition.face_encodings(rgb_small_frame, [face_location])
        
        if not face_encodings:
            return
            
        current_encoding = face_encodings[0]
        
        # Comparar con el embedding conocido
        if self.known_embedding is not None:
            distance = face_recognition.face_distance([self.known_embedding], current_encoding)[0]
            tolerance = 0.5  # Ajustable según necesidad
            
            # Escalar coordenadas al frame original
            top *= 4; right *= 4; bottom *= 4; left *= 4
            
            if distance <= tolerance:
                # VERIFICACIÓN EXITOSA
                confidence = (1 - distance) * 100
                color = (0, 255, 0)  # Verde
                text = f"VERIFICADO ({confidence:.1f}%)"
                status_text = f"¡Verificación exitosa! Confianza: {confidence:.1f}%"
                status_color = "#27ae60"
                
                # Marcar como exitoso y cerrar después de un breve delay
                if not self.verification_successful:
                    self.verification_successful = True
                    QTimer.singleShot(1500, self.accept_verification)  # 1.5 segundos delay
                    
            else:
                # VERIFICACIÓN FALLIDA
                confidence = distance * 100
                color = (0, 0, 255)  # Rojo
                text = f"NO COINCIDE ({confidence:.1f}%)"
                status_text = f"Rostro no coincide. Distancia: {confidence:.1f}%"
                status_color = "#e74c3c"
            
            # Dibujar rectángulo y texto
            cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, text, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Actualizar status
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    color: {status_color};
                    padding: 8px;
                    font-weight: 600;
                }}
            """)
    
    def accept_verification(self):
        """Acepta la verificación y cierra el diálogo"""
        self.accept()
    
    def cancel_verification(self):
        """Cancela la verificación"""
        self.reject()
        
    def closeEvent(self, event):
        """Limpiar recursos al cerrar"""
        if self.timer:
            self.timer.stop()
        if self.cap:
            self.cap.release()
        super().closeEvent(event)

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_window()
        print("LoginWindow initialized")
        
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
        from PyQt6.QtWidgets import QCheckBox
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

    # Checkbox para usar cámara

        self.use_camera_checkbox = QCheckBox("Iniciar sesión sin cámara")
        self.use_camera_checkbox.setChecked(True)
        self.use_camera_checkbox.setStyleSheet("font-size: 14px; color: #34495e; margin-bottom: 10px;")

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
        card_layout.addWidget(self.use_camera_checkbox)
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

        self.login_button.setEnabled(False)
        self.login_button.setText("Validando...")

        try:
            response = requests.get('https://grupo7-tpinicial.onrender.com/get-empleados')
            if response.status_code != 200:
                self.show_message("Error al conectar con la API")
                return

            empleados = response.json()
            usuario = next((e for e in empleados if e.get('username') == username), None)

            if not usuario:
                reply = QMessageBox.question(self, "Usuario no encontrado",
                                            "El usuario no existe. ¿Desea registrarse?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.show_register()
                return

            # Verificar contraseña
            if password != usuario.get('password', ''):
                self.show_message("Contraseña incorrecta")
                return

            # Verificar si es empleado temporal
            is_temporal = usuario.get('temporal', False)
            
            if is_temporal:
                # Para empleados temporales: login directo sin verificación facial
                self.show_message(
                    f"¡Bienvenido {usuario['Nombre']} {usuario['Apellido']} (Temporal)!", 
                    "#27ae60"
                )
                self.registrar_checkin(usuario)
                self.login_successful.emit(usuario)
                return
            
            # Para empleados permanentes: verificar face_embedding
            if 'face_embedding' not in usuario or not usuario['face_embedding']:
                self.show_message("El usuario no tiene rostro registrado.")
                return

            # Si el usuario eligió NO usar la cámara, omitir verificación facial
            if self.use_camera_checkbox.isChecked():
                self.show_message(
                    f"¡Bienvenido {usuario['Nombre']} {usuario['Apellido']}! (Sin verificación facial)",
                    "#27ae60"
                )
                self.registrar_checkin(usuario)
                self.login_successful.emit(usuario)
                return

            # Proceder con verificación facial para empleados permanentes
            known_embedding = np.array(usuario['face_embedding'])
            verification_dialog = FacialVerificationDialog(
                self, 
                known_embedding=known_embedding, 
                username=usuario.get('Nombre', username)
            )
            result = verification_dialog.exec()
            if result and verification_dialog.verification_successful:
                self.show_message(
                    f"¡Bienvenido {usuario['Nombre']} {usuario['Apellido']}!", 
                    "#27ae60"
                )
                self.registrar_checkin(usuario)
                self.login_successful.emit(usuario)
                return
            else:
                self.show_message("Verificación facial cancelada o fallida.")
                
        except Exception as e:
            self.show_message(f"Error durante la verificación: {str(e)}")
        finally:
            self.login_button.setEnabled(True)
            self.login_button.setText("Iniciar Sesión")

    def registrar_checkin(self, usuario):
        checkin_data = {
            "EmpleadoID": usuario.get("EmpleadoID"),
            "username": usuario.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckIn"
        }
        try:
            response = requests.post(
                "https://grupo7-tpinicial.onrender.com/register-evento",
                json=checkin_data
            )
            if response.status_code == 200:
                print("CheckIn registrado en la API")
            else:
                print(f"Error al registrar CheckIn: {response.text}")
        except Exception as e:
            print(f"Error de conexión con la API: {e}")
    
    def show_register(self):
        dialog = RegisterDialog(self)
        if dialog.exec():
            self.show_message("Empleado registrado exitosamente. Puede iniciar sesión.", "#27ae60")
    
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.validar_login(username, password):
            QMessageBox.information(self, "Login", "¡Login exitoso!")
            self.status_label.setText("Login exitoso")
            # Aquí puedes continuar con el flujo de tu aplicación
        else:
            QMessageBox.warning(self, "Login", "Usuario o contraseña incorrectos")
            self.status_label.setText("Login fallido")

    def validar_login(self, username, password):
        try:
            response = requests.get('https://grupo7-tpinicial.onrender.com/get-empleados')
            if response.status_code != 200:
                self.status_label.setText("Error al conectar con la API")
                return False
            empleados = response.json()
            for empleado in empleados:
                if empleado.get('username') == username and empleado.get('password') == password:
                    return True
            return False
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
            return False