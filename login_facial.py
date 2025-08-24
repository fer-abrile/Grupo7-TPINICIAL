import cv2 #type: ignore
import face_recognition # type:ignore
import csv
from datetime import datetime
import pickle
import os

class LoginFacial:
    def __init__(self, archivo_usuarios: str = "usuarios/usuarios.pkl", archivo_log: str = "log.csv"):
        """
        Inicializa la clase LoginFacial.
        """
        self.archivo_usuarios = archivo_usuarios
        self.archivo_log = archivo_log
        os.makedirs(os.path.dirname(self.archivo_usuarios), exist_ok=True)
        if os.path.exists(self.archivo_usuarios):
            with open(self.archivo_usuarios, "rb") as f:
                self.usuarios = pickle.load(f)
        else:
            self.usuarios = {}

    def iniciar_login(self):
        """
        Inicia el proceso de login facial.
        """
        self.recargar_usuarios()  # <--- Agrega esta línea
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("No se pudo acceder a la cámara.")
                return
            frame_count = 0
            process_every = 2  # procesar cada 2 frames para mayor fluidez

            nombres = list(self.usuarios.keys())
            encodings = list(self.usuarios.values())

            if not encodings:
                print("No hay usuarios registrados.")
                return

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                if frame_count % process_every != 0:
                    cv2.imshow("Login Facial", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue

                # Reducir tamaño para acelerar
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                nombres_detectados = []

                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(encodings, face_encoding)
                    nombre_detectado = "Desconocido"
                    if True in matches:
                        first_match_index = matches.index(True)
                        nombre_detectado = nombres[first_match_index]
                        # Evitar registrar múltiples veces seguidas
                        if nombre_detectado not in nombres_detectados:
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            with open(self.archivo_log, mode='a', newline='') as f:
                                writer = csv.writer(f)
                                if os.stat(self.archivo_log).st_size == 0:
                                    writer.writerow(["Nombre", "Hora"])
                                writer.writerow([nombre_detectado, now])
                    nombres_detectados.append(nombre_detectado)

                # Mostrar en pantalla
                for (top, right, bottom, left), nombre in zip(face_locations, nombres_detectados):
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, nombre, (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                cv2.imshow("Login Facial", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"Error durante el login facial: {e}")
        finally:
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()

    def registrar_usuario(self, nombre, imagen):
        """
        Registra un nuevo usuario.
        """
        try:
            # Obtener la codificación facial de la imagen
            imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(imagen)
            if not encodings:
                print("No se detectó ningún rostro en la imagen.")
                return
            encoding = encodings[0]

            # Cargar usuarios actuales para no sobrescribir
            if os.path.exists(self.archivo_usuarios):
                with open(self.archivo_usuarios, "rb") as f:
                    usuarios = pickle.load(f)
            else:
                usuarios = {}

            usuarios[nombre] = encoding  # encoding debe ser el array de face_recognition

            with open(self.archivo_usuarios, "wb") as f:
                pickle.dump(usuarios, f)
            self.usuarios = usuarios  # Actualiza el atributo de la instancia
            print(f"Usuario {nombre} registrado con éxito.")
        except Exception as e:
            print(f"Error al registrar usuario: {e}")

    def recargar_usuarios(self):
        """Recarga los usuarios desde el archivo."""
        if os.path.exists(self.archivo_usuarios):
            with open(self.archivo_usuarios, "rb") as f:
                self.usuarios = pickle.load(f)
        else:
            self.usuarios = {}

with open("usuarios/usuarios.pkl", "rb") as f:
    usuarios = pickle.load(f)
print(usuarios)
