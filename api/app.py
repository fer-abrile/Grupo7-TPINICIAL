import os
import json
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Leer la clave privada desde una variable de entorno
firebase_key_json = os.environ.get('FIREBASE_KEY_JSON')
if not firebase_key_json:
    raise Exception("FIREBASE_KEY_JSON no está definida en las variables de entorno.")

cred = credentials.Certificate(json.loads(firebase_key_json))
firebase_admin.initialize_app(cred)
db = firestore.client()

#Test API
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'})

@app.route('/get-data', methods=['GET'])
def get_data():
    # Cambia 'tu_coleccion' por el nombre de tu colección en Firestore
    docs = db.collection('eventos').stream()
    data = [doc.to_dict() for doc in docs]
    return jsonify(data)

@app.route('/get-empleados', methods=['GET'])
def get_empleados():
    empleados = db.collection('empleados').stream()
    data = [doc.to_dict() for doc in empleados]
    return jsonify(data)

@app.route('/get-fake-empleados', methods=['GET'])
def get_fake_empleados():
    fake_empleados = db.collection('Empleados').stream()
    data = [doc.to_dict() for doc in fake_empleados]
    return jsonify(data)

@app.route('/get-eventos', methods=['GET'])
def get_eventos():
    eventos = db.collection('eventos').stream()
    data = [doc.to_dict() for doc in eventos]
    return jsonify(data)


@app.route('/register-empleado', methods=['POST'])
def register_empleado():
    data = request.get_json()
    required_fields = [
        'Apellido', 'Area', 'EmpleadoID', 'FechaIngreso', 'Nombre',
        'Puesto', 'Turno', 'face_embedding', 'fecha_registro',
        'password', 'username'
    ]
    # Verifica que todos los campos estén presentes
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Falta el campo {field}'}), 400

    db.collection('empleados').add({
        'Apellido': data['Apellido'],
        'Area': data['Area'],
        'EmpleadoID': data['EmpleadoID'],
        'FechaIngreso': data['FechaIngreso'],
        'Nombre': data['Nombre'],
        'Puesto': data['Puesto'],
        'Turno': data['Turno'],
        'face_embedding': data['face_embedding'],
        'fecha_registro': data['fecha_registro'],
        'password': data['password'],
        'username': data['username']
    })
    return jsonify({'message': 'Empleado registrado'})

@app.route('/add-empleado', methods=['POST'])
def add_empleado():
    data = request.get_json()
    
    empleado_data = {
        'Apellido': data.get('Apellido', ''),
        'Area': data.get('Area', ''),
        'EmpleadoID': data.get('EmpleadoID', ''),
        'FechaIngreso': data.get('FechaIngreso', ''),
        'Nombre': data.get('Nombre', ''),
        'Puesto': data.get('Puesto', ''),
        'Turno': data.get('Turno', ''),
        'username': data.get('username', ''),
        'temporal': data.get('temporal', False),
        'face_embedding': data.get('face_embedding', []),
        'password': data.get('password', 'temp123'),  # Default temp password
        'fecha_registro': data.get('fecha_registro', '')
    }
    
    try:
        db.collection('empleados').add(empleado_data)
        return jsonify({'message': 'Empleado agregado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/update-empleado/<empleado_id>', methods=['PUT'])
def update_empleado(empleado_id):
    data = request.get_json()
    
    try:
        # Find the document by EmpleadoID
        empleados_ref = db.collection('empleados')
        query = empleados_ref.where('EmpleadoID', '==', empleado_id).limit(1)
        docs = query.stream()
        
        doc_found = False
        for doc in docs:
            doc_found = True
            doc.reference.update({
                'Apellido': data.get('Apellido', ''),
                'Area': data.get('Area', ''),
                'FechaIngreso': data.get('FechaIngreso', ''),
                'Nombre': data.get('Nombre', ''),
                'Puesto': data.get('Puesto', ''),
                'Turno': data.get('Turno', ''),
                'username': data.get('username', '')
            })
            break
        
        if not doc_found:
            return jsonify({'error': 'Empleado no encontrado'}), 404
            
        return jsonify({'message': 'Empleado actualizado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/delete-empleado/<empleado_id>', methods=['DELETE'])
def delete_empleado(empleado_id):
    try:
        # Find the document by EmpleadoID
        empleados_ref = db.collection('empleados')
        query = empleados_ref.where('EmpleadoID', '==', empleado_id).limit(1)
        docs = query.stream()
        
        doc_found = False
        for doc in docs:
            doc_found = True
            doc.reference.delete()
            break
        
        if not doc_found:
            return jsonify({'error': 'Empleado no encontrado'}), 404
            
        return jsonify({'message': 'Empleado eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register-evento', methods=['POST'])
def register_evento():
    data = request.get_json()
    db.collection('eventos').add(data)
    return jsonify({'message': 'Evento registrado'})


@app.route('/get-productos', methods=['GET'])
def get_productos():
    productos = db.collection('Productos').stream()
    data = []
    for doc in productos:
        prod = doc.to_dict()
        data.append({
            "id": prod.get("id"),
            "nombre": prod.get("nombre"),
            "stock_actual": prod.get("stock_actual")
        })
    return jsonify(data)

@app.route('/get-materias', methods=['GET'])
def get_materias():
    materias = db.collection('MateriaPrima').stream()
    data = []
    for doc in materias:
        mat = doc.to_dict()
        data.append({
            "id": mat.get("id"),
            "nombre": mat.get("nombre"),
            "stock_actual": mat.get("stock_actual")
        })
    return jsonify(data)

@app.route('/get-produccion', methods=['GET'])
def get_produccion():
    try:
        produccion = db.collection('produccion').stream()
        data = [doc.to_dict() for doc in produccion]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/register-produccion', methods=['POST'])
def register_produccion():
    try:
        data = request.get_json()
        db.collection('produccion').add({
            'producto': data.get('producto', ''),
            'cantidad': data.get('cantidad', 0),
            'turno': data.get('turno', ''),
            'timestamp': data.get('timestamp', ''),
            'operario': data.get('operario', '')
        })
        return jsonify({'message': 'Producción registrada correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get-incidencias', methods=['GET'])
def get_incidencias():
    try:
        incidencias = db.collection('incidencias').stream()
        data = [doc.to_dict() for doc in incidencias]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/register-incidencia', methods=['POST'])
def register_incidencia():
    try:
        data = request.get_json()
        db.collection('incidencias').add({
            'tipo': data.get('tipo', ''),
            'prioridad': data.get('prioridad', ''),
            'descripcion': data.get('descripcion', ''),
            'empleado_id': data.get('empleado_id', ''),
            'empleado_nombre': data.get('empleado_nombre', ''),
            'timestamp': data.get('timestamp', ''),
            'estado': data.get('estado', 'Pendiente')
        })
        return jsonify({'message': 'Incidencia registrada correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)