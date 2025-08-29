# test_firestore.py

import firebase_admin
from firebase_admin import credentials, firestore

# 1️⃣ Cargar credenciales
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

# 2️⃣ Obtener cliente de Firestore
db = firestore.client()

# 3️⃣ Crear un documento de prueba
doc_ref = db.collection("test").document("prueba")
doc_ref.set({"mensaje": "¡Conexión exitosa!"})

# 4️⃣ Leer el documento
doc = doc_ref.get()
if doc.exists:
    print("Documento leído:", doc.to_dict())
else:
    print("No se pudo leer el documento")
