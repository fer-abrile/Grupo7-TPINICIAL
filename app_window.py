from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QInputDialog, QMessageBox
)
from PyQt6.QtCore import QTimer
import cv2
import face_recognition
import csv
from datetime import datetime
import os

from registro_datos import RegistroDatos
from login_facial import LoginFacial
from graficos import Graficos

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("App Reconocimiento Facial")
        self.setGeometry(100, 100, 400, 300)

        # Instancias de tus clases
        self.registro = RegistroDatos()
        self.login = LoginFacial()
        self.graficos = Graficos(path_csvs="data/")

        # Atributos para cámara
        self.cap = None
        self.timer = None
        self.reconocido = False

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
        btn_login.clicked.connect(self.iniciar_login)
        layout.addWidget(btn_login)

        btn_graficos = QPushButton("Mostrar Gráficos")
        btn_graficos.clicked.connect(self.mostrar_graficos)
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

    def mostrar_graficos(self):
        self.graficos.menu_graficos()

    # -----------------------------
    # LOGIN FACIAL INTEGRADO
    # -----------------------------
    def iniciar_login(self):
        self.login.recargar_usuarios()
        if not self.login.usuarios:
            QMessageBox.warning(self, "Login", "No hay usuarios registrados.")
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.warning(self, "Login", "No se pudo acceder a la cámara.")
            return

        self.reconocido = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.procesar_frame)
        self.timer.start(30)  # procesar cada 30 ms

    def procesar_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.cap.release()
            return

        # Reducir tamaño para acelerar
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        nombre_detectado = "Desconocido"

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(list(self.login.usuarios.values()), face_encoding)
            nombres = list(self.login.usuarios.keys())
            if True in matches:
                index = matches.index(True)
                nombre_detectado = nombres[index]

                # Guardar log solo una vez
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.login.archivo_log, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    if os.stat(self.login.archivo_log).st_size == 0:
                        writer.writerow(["Nombre", "Hora"])
                    writer.writerow([nombre_detectado, now])
                self.reconocido = True
                break

        # Mostrar mensaje y cerrar cámara automáticamente
        if face_encodings:  # Si detectó al menos un rostro
            if self.reconocido:
                QMessageBox.information(self, "Login", f"Bienvenido {nombre_detectado}!")
            else:
                QMessageBox.warning(self, "Login", "Usuario desconocido")

            self.timer.stop()
            self.cap.release()
