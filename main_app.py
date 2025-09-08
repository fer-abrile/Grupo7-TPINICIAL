import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from login_window import LoginWindow
from main_window import MainWindow
from roled_based_windows import WindowFactory
from datetime import datetime

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user_window = None
        self.usuario_data = None
        self.setup_app_settings()
        
    def setup_app_settings(self):
        """Configuración inicial de la aplicación"""
        self.setWindowTitle("Sistema de Gestión Empresarial")
        # Ocultar la ventana principal ya que usaremos las ventanas específicas por rol
        self.hide()

    def realizar_checkin(self, empleado_data):
        """Realizar check-in del empleado (delega a ApiService en una implementación real)"""
        checkin_data = {
            "EmpleadoID": empleado_data.get("EmpleadoID"),
            "username": empleado_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckIn"
        }
        # Aquí deberías llamar a ApiService.register_evento(checkin_data)
        return True  

    def realizar_checkout(self, empleado_data):
        """Realizar check-out del empleado (delega a ApiService en una implementación real)"""
        checkout_data = {
            "EmpleadoID": empleado_data.get("EmpleadoID"),
            "username": empleado_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckOut"
        }
        # Aquí deberías llamar a ApiService.register_evento(checkout_data)
        return True  

    def cerrar_ventana_actual(self):
        """Cerrar la ventana actual del usuario"""
        if self.current_user_window:
            self.current_user_window.close()
            self.current_user_window = None
            self.usuario_data = None


def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Crear instancia principal de la aplicación
    main_app = MainApp()
    
    # Crear ventana de login
    login_window = LoginWindow()

    def on_login_success(usuario_data):
        """Callback cuando el login es exitoso"""
        try:
            main_app.usuario_data = usuario_data

            # Registrar CheckIn automáticamente
            main_app.realizar_checkin(usuario_data)
            
            # Crear ventana específica según el rol
            puesto = usuario_data.get('Puesto', '').lower()
            print(f"Creando ventana para puesto: {puesto}")
            
            user_window = WindowFactory.create_window(usuario_data)
            
            if user_window:
                main_app.current_user_window = user_window
                user_window.show()
                login_window.close()
                
                def on_user_window_closed():
                    if main_app.usuario_data:
                        main_app.realizar_checkout(main_app.usuario_data)
                    main_app.cerrar_ventana_actual()
                    app.quit()
                
                user_window.destroyed.connect(on_user_window_closed)
                
                app.main_app = main_app
                app.user_window = user_window
            else:
                # Fallback a ventana principal si no se puede crear ventana específica
                print("Usando ventana principal como fallback")
                main_window = MainWindow(usuario_data)
                main_app.current_user_window = main_window
                main_window.show()
                login_window.close()
                app.main_window = main_window
            
        except Exception as e:
            print(f"Error al crear ventana para usuario: {e}")
            QMessageBox.critical(
                login_window,
                "Error",
                f"Error al inicializar la aplicación: {str(e)}\n"
                "Inténtalo de nuevo o contacta al administrador."
            )
    
    def on_login_failed(error_message):
        """Callback cuando el login falla"""
        QMessageBox.warning(login_window, "Error de Login", error_message)
    
    login_window.login_successful.connect(on_login_success)
    if hasattr(login_window, 'login_failed'):
        login_window.login_failed.connect(on_login_failed)
    
    login_window.show()
    
    def cleanup_on_exit():
        """Limpieza al salir de la aplicación"""
        if hasattr(app, 'main_app') and app.main_app.usuario_data:
            app.main_app.realizar_checkout(app.main_app.usuario_data)
        print("Aplicación cerrada correctamente")
    
    app.aboutToQuit.connect(cleanup_on_exit)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()