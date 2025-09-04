import sys
from PyQt6.QtWidgets import QApplication
from login_window import LoginWindow
from main_window import MainWindow
from firebase_manager import FirebaseManager 

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    login_window = LoginWindow()
    
    def on_login_success(usuario_data):
        face_cam = MainWindow(usuario_data, login_window.firebase_manager)
        face_cam.show()
        login_window.close()
        app.face_cam = face_cam 

    login_window.login_successful.connect(on_login_success)
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()