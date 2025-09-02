import requests
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

class SheetToFirebase:
    def __init__(self, firebase_key="firebase_key.json"):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(firebase_key)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"Error conectando a Firebase: {str(e)}")
            self.db = None

    def exportar_sheet(self, spreadsheet_id):
        """
        Exporta todas las hojas de un Google Sheet a Firebase.
        Cada hoja se guarda como una colección con su nombre.
        """
        try:
            # Descargar todo el Sheet en formato Excel
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=xlsx"
            r = requests.get(url)
            r.raise_for_status()

            # Guardar como archivo temporal
            with open("temp.xlsx", "wb") as f:
                f.write(r.content)

            # Leer todas las hojas
            xls = pd.ExcelFile("temp.xlsx")

            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)

                # Subir cada fila como documento
                for i, fila in df.iterrows():
                    self.db.collection(sheet).document(str(i)).set(fila.to_dict())

                print(f"✅ Hoja '{sheet}' exportada a colección '{sheet}' en Firebase")

            return True
        except Exception as e:
            print(f"❌ Error exportando Sheet: {e}")
            return False


# -------------------------
# Bloque ejecutable
# -------------------------
if __name__ == "__main__":
    # Reemplaza con el ID de tu Google Sheet
    SPREADSHEET_ID = "1yMo0LFBWSzG3a3C0WzkIDZlXSrOm0O8q"

    # Crear instancia del exportador
    exportador = SheetToFirebase(firebase_key="firebase_key.json")

    # Exportar todas las hojas a Firebase
    exportador.exportar_sheet(SPREADSHEET_ID)
