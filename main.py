from registro_datos import RegistroDatos
from login_facial import LoginFacial
from graficos import Graficos

def main():
    registro = RegistroDatos()
    login = LoginFacial()
    graficos = Graficos(path_csvs="data/")
 # si los CSV están en la misma carpeta, "" está bien

    while True:
        print("\n--- Menú ---")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Mostrar gráficos")
        print("4. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            nombre = input("Ingresa tu nombre: ")
            registro.registrar_usuario(nombre)
        elif opcion == "2":
            login.iniciar_login()
        elif opcion == "3":
            graficos.menu_graficos()
        elif opcion == "4":
            print("Saliendo...")
            break
        else:
            print("Opción inválida")

if __name__ == "__main__":
    main()
