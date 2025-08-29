import sys
from PyQt6.QtWidgets import QApplication
from login_window import LoginWindow

def main():
    app = QApplication(sys.argv)
    
    # Aplicar tema moderno
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana de login
    login_window = LoginWindow()
    
    # Conectar señal de login exitoso (opcional)
    def on_login_success(usuario_data):
        print(f"Login exitoso para: {usuario_data}")
        # Aquí puedes abrir la ventana principal de la aplicación
    
    login_window.login_successful.connect(on_login_success)
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()