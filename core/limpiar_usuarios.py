import pickle
import os

archivo_usuarios = "usuarios/usuarios.pkl"

# Sobrescribe el archivo con un diccionario vacío
os.makedirs(os.path.dirname(archivo_usuarios), exist_ok=True)
with open(archivo_usuarios, "wb") as f:
    pickle.dump({}, f)

print("Archivo usuarios.pkl limpiado correctamente.")