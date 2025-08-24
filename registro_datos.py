import cv2
import face_recognition
import pickle
import os
from usuario import Usuario

class RegistroDatos:
    def __init__(self, archivo_usuarios="usuarios/usuarios.pkl"):
        self.archivo_usuarios = archivo_usuarios
        os.makedirs(os.path.dirname(self.archivo_usuarios), exist_ok=True)
        if os.path.exists(self.archivo_usuarios):
            with open(self.archivo_usuarios, "rb") as f:
                self.usuarios = pickle.load(f)
        else:
            self.usuarios = {}

    def registrar_usuario(self, nombre):
        cap = cv2.VideoCapture(0)
        # Optimización: reducir resolución de la cámara
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            print("No se pudo abrir la cámara.")
            return

        print("Mostrando cámara, presiona 'q' para capturar tu rostro")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("No se pudo leer el frame de la cámara.")
                break
            cv2.imshow("Registro", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # Reducir tamaño para acelerar
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(rgb_small_frame)
                if encodings:
                    self.usuarios[nombre] = encodings[0]
                    with open(self.archivo_usuarios, "wb") as f:
                        pickle.dump(self.usuarios, f)
                    print(f"{nombre} registrado correctamente")
                else:
                    print("No se detectó rostro, intenta de nuevo")
                break
        cap.release()
        cv2.destroyAllWindows()