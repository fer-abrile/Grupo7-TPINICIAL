Sistema de Gestión Empresarial - Grupo 7
Este proyecto es una aplicación de escritorio desarrollada en Python con PyQt6, orientada a la gestión de empleados y control de acceso biométrico mediante reconocimiento facial. El sistema está diseñado para empresas que requieren registro de asistencia, control de turnos y gestión de roles administrativos.

Características principales
Login con reconocimiento facial: Permite a los empleados iniciar sesión usando su rostro, con opción de login tradicional (usuario/contraseña).
Registro de empleados: Captura de datos personales, área, puesto, turno y rostro biométrico.
Paneles por rol: Interfaz adaptada según el rol del usuario (Operario, Encargado, Supervisor, Administrativo, Administrador).
Check-in y Check-out: Registro automático de entrada y salida de empleados.
Gráficos y estadísticas: Visualización de cumplimiento de turnos y otros indicadores usando matplotlib.
Integración con API: Comunicación con backend remoto para registro y consulta de empleados.
Instalador multiplataforma: Generación de ejecutables para Windows y Linux usando PyInstaller.
Tecnologías utilizadas
Python 3.11+
PyQt6 (interfaz gráfica)
face_recognition y dlib (biometría facial)
matplotlib (gráficos)
numpy (cálculos numéricos)
requests (API REST)
PyInstaller (empaquetado)
API REST en Render
Instalación y ejecución
Windows
Descarga el archivo .exe desde la carpeta dist.
Haz doble clic para ejecutar. No requiere instalación de Python ni dependencias.
Todos los modelos de reconocimiento facial (.dat) están incluidos automáticamente.
Linux
Clona el repositorio y asegúrate de tener Python y las dependencias instaladas.
Ejecuta PyInstaller en Linux para generar el ejecutable nativo.
Usa el comando:
Requisitos
Windows 10/11 o Linux
Cámara web para reconocimiento facial
Acceso a internet para comunicación con la API
Uso
Inicia la aplicación y selecciona el método de login.
Registra nuevos empleados desde el panel administrativo.
Realiza check-in y check-out según el turno.
Visualiza estadísticas y gráficos en los paneles correspondientes.
Notas
El ejecutable es portable y puede compartirse con otros usuarios de Windows.
Para Linux, compila el ejecutable en una máquina Linux.
Los modelos .dat de dlib deben estar en la ruta face_recognition_models/models dentro del ejecutable.
Licencia
Este proyecto es de uso académico y no comercial.
