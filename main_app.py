import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from login_window import LoginWindow
from main_window import MainWindow

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # ...tu inicialización...

    def obtener_empleados(self):
        try:
            response = requests.get('http://localhost:5000/get-empleados')
            if response.status_code == 200:
                return response.json()
            else:
                QMessageBox.warning(self, "Error", "No se pudieron obtener los empleados.")
                return []
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error de conexión: {e}")
            return []

    def registrar_evento(self, evento_data):
        try:
            response = requests.post('http://localhost:5000/register-evento', json=evento_data)
            if response.status_code == 200:
                print("Evento registrado en la API")
            else:
                print(f"Error al registrar evento: {response.text}")
        except Exception as e:
            print(f"Error de conexión con la API: {e}")

    def registrar_empleado(self, empleado_data):
        try:
            response = requests.post('http://localhost:5000/register-empleado', json=empleado_data)
            if response.status_code == 200:
                print("Empleado registrado en la API")
            else:
                print(f"Error al registrar empleado: {response.text}")
        except Exception as e:
            print(f"Error de conexión con la API: {e}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    login_window = LoginWindow()
    
    def on_login_success(usuario_data):
        face_cam = MainWindow(usuario_data)
        face_cam.show()
        login_window.close()
        app.face_cam = face_cam 

    login_window.login_successful.connect(on_login_success)
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()