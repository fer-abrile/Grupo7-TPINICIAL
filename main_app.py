import sys
from PyQt6.QtWidgets import QApplication
from login_window import LoginWindow
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    login_window = LoginWindow()

    def on_login_success(usuario_data):
        main_window = MainWindow(usuario_data)
        main_window.show()
        login_window.close()

    login_window.login_successful.connect(on_login_success)
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()