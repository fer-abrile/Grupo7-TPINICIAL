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
    def __init__(self, parent=None, known_embedding=None):
        super().__init__(parent)
        self.known_embedding = known_embedding  # Para modo verificación
        self.is_verification_mode = known_embedding is not None
        
        if self.is_verification_mode:
            self.setWindowTitle("Verificación de Rostro")
        else:
            self.setWindowTitle("Captura de Rostro")
            
        self.setModal(True)
        self.setFixedSize(640, 550)
        self.captured_frame = None
        self.face_embedding = None
        self.verification_successful = False

        self.setup_ui()
        self.start_camera()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título descriptivo
        if self.is_verification_mode:
            title_text = "Verifique su identidad mirando a la cámara"
        else:
            title_text = "Capture su rostro para el registro"
            
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
                padding: 10px;
                background-color: rgba(52, 152, 219, 0.1);
                border-radius: 8px;
            }
        """)
        layout.addWidget(title)

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
        self.status_label = QLabel("Posicione su rostro frente a la cámara")
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

        btn_layout = QHBoxLayout()
        
        if not self.is_verification_mode:  # Solo mostrar botón capturar en modo registro
            self.capture_btn = ModernButton("Capturar Rostro", "primary")
            self.capture_btn.clicked.connect(self.capture_face)
            btn_layout.addWidget(self.capture_btn)
            
        self.cancel_btn = ModernButton("Cancelar", "danger")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "No se puede acceder a la cámara")
            self.reject()
            return
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            
            # Si estamos en modo verificación, procesar automáticamente
            if self.is_verification_mode:
                self.process_verification(frame)
            else:
                # En modo captura, solo mostrar el video
                self.draw_face_detection_guide(frame)
            
            # Mostrar frame en la interfaz
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.video_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)
            
    def draw_face_detection_guide(self, frame):
        """Dibuja guías visuales para ayudar en la captura"""
        # Detectar caras para mostrar guías
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        
        if face_locations:
            for face_location in face_locations:
                top, right, bottom, left = face_location
                top *= 4; right *= 4; bottom *= 4; left *= 4
                
                # Dibujar rectángulo azul para guía
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 165, 0), 2)
                cv2.putText(frame, "ROSTRO DETECTADO", (left, top - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            
            self.status_label.setText("Rostro detectado. Haga clic en 'Capturar' cuando esté listo.")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #27ae60;
                    padding: 8px;
                    font-weight: 600;
                }
            """)
        else:
            self.status_label.setText("Posicione su rostro frente a la cámara")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #f39c12;
                    padding: 8px;
                    font-weight: 500;
                }
            """)

    def process_verification(self, frame):
        """Procesa la verificación facial en tiempo real"""
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        
        if not face_locations:
            self.status_label.setText("No se detecta rostro")
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
            self.status_label.setText("Múltiples rostros detectados")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #e74c3c;
                    padding: 8px;
                    font-weight: 500;
                }
            """)
            return
        
        # Procesar la única cara detectada
        face_location = face_locations[0]
        face_encodings = face_recognition.face_encodings(rgb_small_frame, [face_location])
        
        if face_encodings:
            current_encoding = face_encodings[0]
            distance = face_recognition.face_distance([self.known_embedding], current_encoding)[0]
            
            top, right, bottom, left = face_location
            top *= 4; right *= 4; bottom *= 4; left *= 4
            
            if distance <= 0.5:  # Tolerancia ajustable
                confidence = (1 - distance) * 100
                color = (0, 255, 0)
                text = f"VERIFICADO ({confidence:.1f}%)"
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, text, (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                self.status_label.setText(f"¡Verificación exitosa! ({confidence:.1f}%)")
                self.status_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        color: #27ae60;
                        padding: 8px;
                        font-weight: 600;
                    }
                """)


    def capture_face(self):
        """Captura el rostro para registro (modo no-verificación)"""
        if hasattr(self, 'current_frame'):
            # Procesar el frame para detectar rostros
            rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            rgb_frame = np.ascontiguousarray(rgb_frame, dtype=np.uint8)
            face_locations = face_recognition.face_locations(rgb_frame)

            if len(face_locations) == 1:
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                if face_encodings:
                    self.face_embedding = face_encodings[0].tolist()
                    
                    # Dibujar rectángulo de confirmación
                    top, right, bottom, left = face_locations[0]
                    cv2.rectangle(self.current_frame, (left, top), (right, bottom), (0, 255, 0), 3)
                    cv2.putText(self.current_frame, "CAPTURADO", (left, top - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    
                    QMessageBox.information(self, "Éxito", "Rostro capturado correctamente.")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo procesar el rostro.")
            elif len(face_locations) == 0:
                QMessageBox.warning(self, "Advertencia", "No se detectó ningún rostro. Intente de nuevo.")
            else:
                QMessageBox.warning(self, "Advertencia", "Se detectaron múltiples rostros. Intente de nuevo.")

    def closeEvent(self, event):
        """Limpiar recursos al cerrar"""
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        super().closeEvent(event)


class RegisterDialog(QDialog):
    def __init__(self, parent, firebase_manager):
        super().__init__(parent)
        self.firebase_manager = firebase_manager
        self.setWindowTitle("Registro de Empleado")
        self.setFixedSize(650, 650)  # Más ancho y alto
        self.setModal(True)
        self.face_embedding = None
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)  # Más margen horizontal
        
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
        form_layout.setSpacing(18)  # Más espacio entre campos
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        self.nombre_edit = ModernLineEdit("Nombre")
        self.apellido_edit = ModernLineEdit("Apellido")
        self.area_combo = QComboBox()
        self.area_combo.addItems(["Control de Calidad", "Distribucion", "Produccion", "Logistica","Administracion","Sistemas"])
        combo_style = ("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 10px;
                padding: 12px 15px;
                padding-right: 30px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #3498db;
                border-left-style: solid;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(52, 152, 219, 0.1), stop:1 rgba(52, 152, 219, 0.2));
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 8px;
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #3498db;
                margin-right: 2px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #2980b9;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                padding: 5px;
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
                padding-right: 30px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #3498db;
                border-left-style: solid;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(52, 152, 219, 0.1), stop:1 rgba(52, 152, 219, 0.2));
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #3498db;
                margin-right: 5px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #2980b9;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                padding: 5px;
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
                padding-right: 30px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #3498db;
                border-left-style: solid;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(52, 152, 219, 0.1), stop:1 rgba(52, 152, 219, 0.2));
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 8px;
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #3498db;
                margin-right: 2px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #2980b9;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                padding: 5px;
            }
        """)
        
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        date_style = ("""
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
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #3498db;
                border-left-style: solid;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
        }
            QDateEdit::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #3498db;
        }
        """)

        self.area_combo.setStyleSheet(combo_style)
        self.puesto_combo.setStyleSheet(combo_style)
        self.turno_combo.setStyleSheet(combo_style)
        
        # Aplicar estilo al DateEdit
        self.fecha_edit.setStyleSheet(date_style)

        form_layout.addRow("Nombre:", self.nombre_edit)
        form_layout.addRow("Apellido:", self.apellido_edit)
        form_layout.addRow("Área:", self.area_combo)
        form_layout.addRow("Puesto:", self.puesto_combo)
        form_layout.addRow("Fecha Ingreso:", self.fecha_edit)
        form_layout.addRow("Turno:", self.turno_combo)
        
        layout.addLayout(form_layout)
        
        # Botón para capturar rostro
        self.capture_face_button = ModernButton("📷 Capturar Rostro", "primary")
        self.capture_face_button.clicked.connect(self.open_camera_popup)
        layout.addWidget(self.capture_face_button)
        
        # Indicador de estado de captura
        self.capture_status = QLabel("❌ Rostro no capturado")
        self.capture_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capture_status.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #e74c3c;
                padding: 5px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.capture_status)
        
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
        """Abre el popup de cámara en modo captura (no verificación)"""
        popup = CameraPopup(self)  # Sin known_embedding = modo captura
        if popup.exec():
            self.face_embedding = popup.face_embedding
            # Actualizar indicador visual
            self.capture_status.setText("✅ Rostro capturado correctamente")
            self.capture_status.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #27ae60;
                    padding: 5px;
                    font-weight: 600;
                }
            """)
            self.capture_face_button.setText("🔄 Recapturar Rostro")

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
        
        if self.firebase_manager.db and self.firebase_manager.registrar_usuario(datos_usuario):
            QMessageBox.information(self, "Éxito", 
                f"Empleado registrado exitosamente.\nEmpleadoID: {empleado_id}\nUsername: {username}\nContraseña: 12345")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Error al registrar el empleado")
                
            if not self.verification_successful:
                    self.verification_successful = True
                    QTimer.singleShot(1500, self.accept)
                    
            else:
                confidence = distance * 100
                color = (0, 0, 255)
                text = f"NO COINCIDE ({confidence:.1f}%)"
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, text, (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                self.status_label.setText("Rostro no coincide")
                self.status_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        color: #e74c3c;
                        padding: 8px;
                        font-weight: 600;
                    }
                """)
                