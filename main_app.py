import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer
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

    def obtener_empleados(self):
        """Obtener lista de empleados desde la API"""
        try:
            response = requests.get('http://localhost:5000/get-empleados')
            if response.status_code == 200:
                return response.json()
            else:
                QMessageBox.warning(None, "Error", "No se pudieron obtener los empleados.")
                return []
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error de conexión con la API: {e}")
            return []

    def obtener_empleados_fake(self):
        """Obtener empleados de la colección fake (para testing)"""
        try:
            response = requests.get('http://localhost:5000/get-fake-empleados')
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            print(f"Error obteniendo empleados fake: {e}")
            return []

    def verificar_conexion_api(self):
        """Verificar si la API está disponible"""
        try:
            response = requests.get('http://localhost:5000/ping', timeout=5)
            return response.status_code == 200 and response.json().get('message') == 'pong'
        except Exception as e:
            print(f"Error verificando conexión API: {e}")
            return False

    def registrar_evento(self, evento_data):
        """Registrar evento (CheckIn/CheckOut) en la API"""
        try:
            response = requests.post('http://localhost:5000/register-evento', json=evento_data)
            if response.status_code == 200:
                print("Evento registrado en la API")
                return True
            else:
                print(f"Error al registrar evento: {response.text}")
                return False
        except Exception as e:
            print(f"Error de conexión con la API al registrar evento: {e}")
            return False

    def registrar_empleado(self, empleado_data):
        """Registrar nuevo empleado en la API"""
        try:
            response = requests.post('http://localhost:5000/register-empleado', json=empleado_data)
            if response.status_code == 200:
                print("Empleado registrado en la API")
                return True
            else:
                print(f"Error al registrar empleado: {response.text}")
                return False
        except Exception as e:
            print(f"Error de conexión con la API al registrar empleado: {e}")
            return False

    def agregar_empleado(self, empleado_data):
        """Agregar empleado usando el endpoint add-empleado"""
        try:
            # Si es temporal, establecer password por defecto
            if empleado_data.get('temporal', False):
                empleado_data['password'] = '12345'
                empleado_data['face_embedding'] = []  # Sin reconocimiento facial
                
            response = requests.post('http://localhost:5000/add-empleado', json=empleado_data)
            if response.status_code == 200:
                print("Empleado agregado correctamente")
                return True
            else:
                print(f"Error al agregar empleado: {response.text}")
                return False
        except Exception as e:
            print(f"Error de conexión al agregar empleado: {e}")
            return False

    def actualizar_empleado(self, empleado_id, empleado_data):
        """Actualizar empleado existente"""
        try:
            response = requests.put(f'http://localhost:5000/update-empleado/{empleado_id}', json=empleado_data)
            if response.status_code == 200:
                print("Empleado actualizado correctamente")
                return True
            else:
                print(f"Error al actualizar empleado: {response.text}")
                return False
        except Exception as e:
            print(f"Error de conexión al actualizar empleado: {e}")
            return False

    def eliminar_empleado(self, empleado_id):
        """Eliminar empleado"""
        try:
            response = requests.delete(f'http://localhost:5000/delete-empleado/{empleado_id}')
            if response.status_code == 200:
                print("Empleado eliminado correctamente")
                return True
            else:
                print(f"Error al eliminar empleado: {response.text}")
                return False
        except Exception as e:
            print(f"Error de conexión al eliminar empleado: {e}")
            return False

    def obtener_productos(self):
        """Obtener lista de productos"""
        try:
            response = requests.get('http://localhost:5000/get-productos')
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            print(f"Error obteniendo productos: {e}")
            return []

    def obtener_materias_primas(self):
        """Obtener lista de materias primas"""
        try:
            response = requests.get('http://localhost:5000/get-materias')
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            print(f"Error obteniendo materias primas: {e}")
            return []

    def obtener_produccion(self):
        """Obtener datos de producción"""
        try:
            response = requests.get('http://localhost:5000/get-produccion')
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            print(f"Error obteniendo datos de producción: {e}")
            return []

    def registrar_produccion(self, produccion_data):
        """Registrar datos de producción"""
        try:
            response = requests.post('http://localhost:5000/register-produccion', json=produccion_data)
            if response.status_code == 200:
                print("Producción registrada correctamente")
                return True
            else:
                print(f"Error al registrar producción: {response.text}")
                return False
        except Exception as e:
            print(f"Error de conexión al registrar producción: {e}")
            return False

    def obtener_incidencias(self):
        """Obtener lista de incidencias"""
        try:
            response = requests.get('http://localhost:5000/get-incidencias')
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            print(f"Error obteniendo incidencias: {e}")
            return []

    def registrar_incidencia(self, incidencia_data):
        """Registrar nueva incidencia"""
        try:
            response = requests.post('http://localhost:5000/register-incidencia', json=incidencia_data)
            if response.status_code == 200:
                print("Incidencia registrada correctamente")
                return True
            else:
                print(f"Error al registrar incidencia: {response.text}")
                return False
        except Exception as e:
            print(f"Error de conexión al registrar incidencia: {e}")
            return False

    def obtener_eventos(self):
        """Obtener eventos de asistencia"""
        try:
            response = requests.get('http://localhost:5000/get-eventos')
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            print(f"Error obteniendo eventos: {e}")
            return []

    def realizar_checkin(self, empleado_data):
        """Realizar check-in del empleado"""
        checkin_data = {
            "EmpleadoID": empleado_data.get("EmpleadoID"),
            "username": empleado_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckIn"
        }
        return self.registrar_evento(checkin_data)

    def realizar_checkout(self, empleado_data):
        """Realizar check-out del empleado"""
        checkout_data = {
            "EmpleadoID": empleado_data.get("EmpleadoID"),
            "username": empleado_data.get("username"),
            "timestamp": datetime.now().isoformat(),
            "evento": "CheckOut"
        }
        return self.registrar_evento(checkout_data)

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
    
    # Verificar conexión con la API al iniciar
    if not main_app.verificar_conexion_api():
        reply = QMessageBox.critical(
            None, 
            "Error de Conexión", 
            "No se puede conectar con el servidor API.\n"
            "¿Deseas continuar en modo offline?\n\n"
            "Funcionalidades limitadas estarán disponibles.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            sys.exit(1)
    
    # Crear ventana de login
    login_window = LoginWindow()
    
    def on_login_success(usuario_data):
        """Callback cuando el login es exitoso"""
        try:
            # Guardar datos del usuario en la instancia principal
            main_app.usuario_data = usuario_data
            
            # Registrar CheckIn automáticamente
            if main_app.realizar_checkin(usuario_data):
                print("CheckIn registrado automáticamente")
            
            # Crear ventana específica según el rol usando WindowFactory
            puesto = usuario_data.get('Puesto', '').lower()
            print(f"Creando ventana para puesto: {puesto}")
            
            # Usar WindowFactory para crear la ventana apropiada
            user_window = WindowFactory.create_window(usuario_data)
            
            if user_window:
                main_app.current_user_window = user_window
                user_window.show()
                login_window.close()
                
                # Configurar el cierre de la aplicación cuando se cierre la ventana del usuario
                def on_user_window_closed():
                    # Realizar checkout automático al cerrar
                    if main_app.usuario_data:
                        main_app.realizar_checkout(main_app.usuario_data)
                    main_app.cerrar_ventana_actual()
                    app.quit()
                
                user_window.destroyed.connect(on_user_window_closed)
                
                # Mantener referencia en la aplicación principal
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
    
    # Conectar señales del login
    login_window.login_successful.connect(on_login_success)
    if hasattr(login_window, 'login_failed'):
        login_window.login_failed.connect(on_login_failed)
    
    # Mostrar ventana de login
    login_window.show()
    
    # Configurar manejo de cierre de aplicación
    def cleanup_on_exit():
        """Limpieza al salir de la aplicación"""
        if hasattr(app, 'main_app') and app.main_app.usuario_data:
            app.main_app.realizar_checkout(app.main_app.usuario_data)
        print("Aplicación cerrada correctamente")
    
    app.aboutToQuit.connect(cleanup_on_exit)
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
        main()