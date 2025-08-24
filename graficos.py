# graficos.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

class Graficos:
    def __init__(self, path_csvs="", interactive=False):
        """Inicializa la clase con la ruta donde están los CSV"""
        self.path = path_csvs
        self.interactive = interactive  # Permite mostrar gráficos si True
        self.productos = pd.read_csv(f"{self.path}Producto.csv")
        self.produccion = pd.read_csv(f"{self.path}Produccion.csv")
        self.eventos = pd.read_csv(f"{self.path}Eventos.csv")
        self.empleados = pd.read_csv(f"{self.path}Empleado.csv")

    def _mostrar_o_guardar(self, nombre_archivo):
        """Muestra el gráfico si es interactivo o lo guarda en un PNG"""
        if self.interactive:
            plt.show()
        else:
            ruta_guardado = os.path.join(self.path, f"{nombre_archivo}.png")
            plt.savefig(ruta_guardado)
            print(f"Gráfico guardado en: {ruta_guardado}")
            plt.close()

    def produccion_por_producto(self):
        """Grafico de producción total por producto"""
        df = self.produccion.groupby('ProductoID')['CantidadProducida'].sum().reset_index()
        df = df.merge(self.productos, on='ProductoID')
        plt.figure(figsize=(10,6))
        sns.barplot(data=df, x='NombreProducto', y='CantidadProducida', palette='viridis',
                    hue=None, dodge=False)  # Evita FutureWarning
        plt.title("Producción total por producto")
        plt.xticks(rotation=45)
        plt.tight_layout()
        self._mostrar_o_guardar("produccion_por_producto")

    def desperdicio_por_producto(self):
        """Grafico de desperdicio por producto"""
        df = self.produccion.groupby('ProductoID')['CantidadDesperdicio'].sum().reset_index()
        df = df.merge(self.productos, on='ProductoID')
        plt.figure(figsize=(10,6))
        sns.barplot(data=df, x='NombreProducto', y='CantidadDesperdicio', palette='magma',
                    hue=None, dodge=False)
        plt.title("Desperdicio total por producto")
        plt.xticks(rotation=45)
        plt.tight_layout()
        self._mostrar_o_guardar("desperdicio_por_producto")

    def eventos_por_empleado(self):
        """Grafico de cantidad de eventos por empleado"""
        df = self.eventos.groupby('EmpleadoID').size().reset_index(name='CantidadEventos')
        df = df.merge(self.empleados, on='EmpleadoID')
        plt.figure(figsize=(12,6))
        sns.barplot(data=df, x='Nombre', y='CantidadEventos', palette='coolwarm',
                    hue=None, dodge=False)
        plt.title("Cantidad de eventos (ingresos/egresos) por empleado")
        plt.xticks(rotation=45)
        plt.tight_layout()
        self._mostrar_o_guardar("eventos_por_empleado")

    def menu_graficos(self):
        while True:
            print("\n--- Menú de Gráficos ---")
            print("1. Producción por producto")
            print("2. Desperdicio por producto")
            print("3. Eventos por empleado")
            print("4. Volver al menú principal")
            opcion = input("Elige una opción: ")

            if opcion == "1":
                self.produccion_por_producto()
            elif opcion == "2":
                self.desperdicio_por_producto()
            elif opcion == "3":
                self.eventos_por_empleado()
            elif opcion == "4":
                break
            else:
                print("Opción inválida")
