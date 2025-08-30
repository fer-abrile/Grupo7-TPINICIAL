from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox
import cv2
import face_recognition
import csv
from datetime import datetime
import os


class LoginFacial:
    def __init__(self, archivo_usuarios="usuarios/usuarios.pkl", archivo_log="log.csv", parent=None):
        self.parent = parent
        self.archivo_usuarios = archivo_usuarios
        self.archivo_log = archivo_log
        self.usuarios = {}  # nombre -> encoding
        self.cap = None
        self.timer = None
        self.reconocido = False
        self.parent = parent  # referencia a la ventana principal para mostrar QMessageBox

        self.recargar_usuarios()

    def recargar_usuarios(self):
        import pickle
        if os.path.exists(self.archivo_usuarios):
            with open(self.archivo_usuarios, "rb") as f:
                self.usuarios = pickle.load(f)

    # -----------------------------
    # MÉTODO PRINCIPAL DE LOGIN
    # -----------------------------
    def iniciar_login(self, username):
        if not self.usuarios:
            QMessageBox.warning(self.parent, "Login", "No hay usuarios registrados.")
            return False

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.warning(self.parent, "Login", "No se pudo acceder a la cámara.")
            return False

        reconocido = False
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Reducir resolución para procesar más rápido
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Detección de caras
            face_locations = face_recognition.face_locations(rgb_small_frame)
            for face_location in face_locations:
                encodings = face_recognition.face_encodings(
                    rgb_small_frame, known_face_locations=[face_location]
                )[0:1]
                if not encodings:
                    continue

                encoding = encodings[0]

                # Comparar contra los usuarios registrados
                matches = face_recognition.compare_faces(list(self.usuarios.values()), encoding)
                nombres = list(self.usuarios.keys())
                print("resultado",matches,nombres)

                # Escalar coordenadas a la imagen original
                top, right, bottom, left = face_location
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                if True in matches:
                    index = matches.index(True)
                    nombre_detectado = nombres[index]
                    if nombre_detectado == username:
                        text = nombre_detectado
                        color = (125,220,0)
                        reconocido = True
                        self._registrar_log(nombre_detectado)
                    else:
                        text = "Desconocido"
                        color = (50, 50, 255)

                cv2.rectangle(frame, (left, bottom), (right, bottom +30), color, -1)        
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, text, (left, bottom + 20), 2, 0.7, (255, 255, 255), 1)
                break

            cv2.imshow("Reconocimiento Facial", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or reconocido:
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        return reconocido

    def procesar_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self._cerrar_cam()
            return

        # Reducir tamaño para acelerar
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        nombre_detectado = "Desconocido"

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(list(self.usuarios.values()), face_encoding)
            nombres = list(self.usuarios.keys())
            if True in matches:
                index = matches.index(True)
                nombre_detectado = nombres[index]
                self._registrar_log(nombre_detectado)
                self.reconocido = True
                break

        # Mostrar resultado y cerrar
        if face_encodings:
            if not self.reconocido:
               # QMessageBox.information(self.parent, "Login", f"Bienvenido {nombre_detectado}!")
            #else:
                QMessageBox.warning(self.parent, "Login", "Usuario desconocido")

            self._cerrar_cam()

    # -----------------------------
    # MÉTODOS AUXILIARES
    # -----------------------------
    def _cerrar_cam(self):
        if self.timer:
            self.timer.stop()
        if self.cap:
            self.cap.release()

    def _registrar_log(self, nombre_detectado):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.archivo_log, mode="a", newline="") as f:
            writer = csv.writer(f)
            if os.stat(self.archivo_log).st_size == 0:
                writer.writerow(["Nombre", "Hora"])
            writer.writerow([nombre_detectado, now])