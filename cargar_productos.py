import firebase_admin
from firebase_admin import credentials, firestore

# 1. Inicializar Firebase con credenciales
cred = credentials.Certificate("firebase_key.json")  # tu archivo JSON de credenciales
firebase_admin.initialize_app(cred)

# 2. Conexión con Firestore
db = firestore.client()

# 3. Lista de productos
productos = [
    {"id": "P001", "nombre": "Harina 1kg", "stock_actual": 50, "stock_minimo": 20, "estado": "Disponible"},
    {"id": "P002", "nombre": "Azúcar 1kg", "stock_actual": 15, "stock_minimo": 20, "estado": "Bajo Stock"},
    {"id": "P003", "nombre": "Aceite 1L", "stock_actual": 0, "stock_minimo": 10, "estado": "Agotado"},
    {"id": "P004", "nombre": "Arroz 1kg", "stock_actual": 40, "stock_minimo": 15, "estado": "Disponible"},
    {"id": "P005", "nombre": "Leche en polvo", "stock_actual": 8, "stock_minimo": 10, "estado": "Bajo Stock"},
    {"id": "P006", "nombre": "Fideos 500g", "stock_actual": 70, "stock_minimo": 25, "estado": "Disponible"},
    {"id": "P007", "nombre": "Yerba Mate 1kg", "stock_actual": 5, "stock_minimo": 15, "estado": "Bajo Stock"},
    {"id": "P008", "nombre": "Galletitas surtidas", "stock_actual": 0, "stock_minimo": 5, "estado": "Agotado"},
    {"id": "P009", "nombre": "Café 500g", "stock_actual": 22, "stock_minimo": 10, "estado": "Disponible"},
    {"id": "P010", "nombre": "Sal fina 1kg", "stock_actual": 12, "stock_minimo": 10, "estado": "Disponible"}
]

# 4. Subir a Firestore
for p in productos:
    doc_ref = db.collection("productos").document(p["id"])
    doc_ref.set(p)
    print(f"✅ Producto {p['nombre']} agregado con ID {p['id']}")
