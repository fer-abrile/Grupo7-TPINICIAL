from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFormLayout, QComboBox, QDateEdit, QMessageBox, QPushButton, QWidget)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QImage, QPixmap
from datetime import datetime
from modern_components import ModernLineEdit, ModernButton

import cv2
import face_recognition
import numpy as np

class CameraPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Captura de Rostro")
        self.setModal(True)
        self.setFixedSize(500, 500)
        self.captured_frame = None
        self.face_embedding = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.video_label = QLabel()
        self.video_label.setFixedSize(480, 360)
        self.layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capturar")
        self.cancel_btn = QPushButton("Cancelar")
        btn_layout.addWidget(self.capture_btn)
        btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(btn_layout)

        self.capture_btn.clicked.connect(self.capture_face)
        self.cancel_btn.clicked.connect(self.reject)

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def capture_face(self):
        if hasattr(self, 'current_frame'):
            # Asegura que la imagen sea contigua y de tipo uint8
            rgb_frame = self.current_frame[:, :, ::-1].copy()
            rgb_frame = np.ascontiguousarray(rgb_frame, dtype=np.uint8)
            face_locations = face_recognition.face_locations(rgb_frame)
            if len(face_locations) == 1:
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                self.face_embedding = [round(float(x), 5) for x in face_encodings[0]]
                QMessageBox.information(self, "Éxito", "Rostro capturado correctamente.")
                self.accept()
            elif len(face_locations) == 0:
                QMessageBox.warning(self, "Advertencia", "No se detectó ningún rostro. Intente de nuevo.")
            else:
                QMessageBox.warning(self, "Advertencia", "Se detectaron múltiples rostros. Intente de nuevo.")

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        super().closeEvent(event)

class RegisterDialog(QDialog):
    def __init__(self, parent, firebase_manager):
        super().__init__(parent)
        self.firebase_manager = firebase_manager
        self.setWindowTitle("Registro de Empleado")
        self.setFixedSize(500, 600)
        self.setModal(True)
        self.face_embedding = None
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Registro de Empleado")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.nombre_edit = ModernLineEdit("Nombre")
        self.apellido_edit = ModernLineEdit("Apellido")
        self.area_combo = QComboBox()
        self.area_combo.addItems(["Control de Calidad", "Distribucion", "Produccion", "Logistica","Administracion","Sistemas"])
        self.area_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #3498db;
            }
        """)
        self.puesto_combo = QComboBox()
        self.puesto_combo.addItems(["Operario", "Encargado", "Supervisor", "Administrativo","Administrador"])
        self.puesto_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #3498db;
            }

        """)

        self.turno_combo = QComboBox()
        self.turno_combo.addItems(["Mañana", "Tarde", "Noche", "Rotativo"])
        self.turno_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #3498db;
            }
        """)
        
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setStyleSheet("""
            QDateEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QDateEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        form_layout.addRow("Nombre:", self.nombre_edit)
        form_layout.addRow("Apellido:", self.apellido_edit)
        form_layout.addRow("Área:", self.area_combo)
        form_layout.addRow("Puesto:", self.puesto_combo)
        form_layout.addRow("Fecha Ingreso:", self.fecha_edit)
        form_layout.addRow("Turno:", self.turno_combo)
        
        layout.addLayout(form_layout)
        
        # Botón para capturar rostro
        self.capture_face_button = ModernButton("Capturar Rostro", "primary")
        self.capture_face_button.clicked.connect(self.open_camera_popup)
        layout.addWidget(self.capture_face_button)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.save_button = ModernButton("Guardar", "success")
        self.cancel_button = ModernButton("Cancelar", "secondary")
        
        self.save_button.clicked.connect(self.save_employee)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f4fd, stop:1 #f8fbff);
            }
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #34495e;
            }
        """)
    
    def generar_username(self, nombre, apellido):
        if not nombre or not apellido:
            return ""
        return (nombre[0] + apellido).lower()
    
    def open_camera_popup(self):
        popup = CameraPopup(self)
        if popup.exec():
            self.face_embedding = popup.face_embedding

    def save_employee(self):
        if not all([
            self.nombre_edit.text().strip(),
            self.apellido_edit.text().strip(),
            self.area_combo.currentText().strip(),
            self.puesto_combo.currentText().strip()
        ]):
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return

        if self.face_embedding is None:
            QMessageBox.warning(self, "Error", "Debe capturar el rostro antes de guardar.")
            return 
        
        username = self.generar_username(
            self.nombre_edit.text().strip(),
            self.apellido_edit.text().strip()
        )
        
        import time
        timestamp = str(int(time.time()))[-6:]
        empleado_id = f"EMP{timestamp}{self.nombre_edit.text().strip()[:2].upper()}"
        
        datos_usuario = {
            'EmpleadoID': empleado_id,
            'Nombre': self.nombre_edit.text().strip(),
            'Apellido': self.apellido_edit.text().strip(),
            'Area': self.area_combo.currentText().strip(),
            'Puesto': self.puesto_combo.currentText().strip(),
            'FechaIngreso': self.fecha_edit.date().toString('yyyy-MM-dd'),
            'Turno': self.turno_combo.currentText(),
            'username': username,
            'fecha_registro': datetime.now().isoformat(),
            'password':'12345',
            'face_embedding': self.face_embedding
        }
        print(datos_usuario)
        if self.firebase_manager.db and self.firebase_manager.registrar_usuario(datos_usuario):
            QMessageBox.information(self, "Éxito", 
                f"Empleado registrado exitosamente.\nEmpleadoID: {empleado_id}\nUsername: {username}")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Error al registrar el empleado")