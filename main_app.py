import sys
from PyQt6.QtWidgets import QApplication
from login_window import LoginWindow
from face_cam import MainWindow  # <-- Importa la ventana principal

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    login_window = LoginWindow()
    
    def on_login_success(usuario_data):
        print(f"Login exitoso para: {usuario_data}")
        face_cam = MainWindow(usuario_data)
        face_cam.show()
        login_window.close()
        app.face_cam = face_cam  # Mantén la referencia

    login_window.login_successful.connect(on_login_success)
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()