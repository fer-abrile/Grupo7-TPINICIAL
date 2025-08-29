import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

class FirebaseManager:
    def __init__(self):
        try:
            if not firebase_admin._apps:
                # Reemplaza con la ruta a tu archivo de credenciales JSON
                cred = credentials.Certificate("firebase_key.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"Error conectando a Firebase: {str(e)}")
            self.db = None
    
    def buscar_usuario(self, username):
        """Busca un usuario por username en Firestore"""
        try:
            users_ref = self.db.collection('empleados')
            query = users_ref.where('username', '==', username).limit(1)
            docs = query.stream()
            
            for doc in docs:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error buscando usuario: {e}")
            return None
    
    def registrar_usuario(self, datos_usuario):
        """Registra un nuevo usuario en Firestore"""
        try:
            doc_ref = self.db.collection('empleados').document()
            doc_ref.set(datos_usuario)
            return True
        except Exception as e:
            print(f"Error registrando usuario: {e}")
            return False