import os
import json
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Leer la clave privada desde un archivo secreto en Render
firebase_key_path = '/etc/secrets/firebase_key.json'
if os.path.exists(firebase_key_path):
    with open(firebase_key_path) as f:
        firebase_key_json = json.load(f)
else:
    # Fallback: leer desde variable de entorno (útil para desarrollo local)
    firebase_key_env = os.environ.get('FIREBASE_KEY_JSON')
    if not firebase_key_env:
        raise Exception("No se encontró la clave privada de Firebase ni en /etc/secrets/firebase_key.json ni en la variable de entorno FIREBASE_KEY_JSON.")
    firebase_key_json = json.loads(firebase_key_env)

cred = credentials.Certificate(firebase_key_json)
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
        'password': data.get('password', '12345'),
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
    try:
        productos = db.collection('productos').stream()
        data = []
        for doc in productos:
            prod = doc.to_dict()
            print(f"Producto encontrado: {prod}")  # Debug line
            data.append({
                "id": prod.get("id"),
                "nombre": prod.get("nombre"),
                "stock_actual": prod.get("stock_actual", 0),
                "stock_minimo": prod.get("stock_minimo", 0)
            })
        print(f"Total productos: {len(data)}")  # Debug line
        return jsonify(data)
    except Exception as e:
        print(f"Error getting productos: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
    
@app.route('/update-stock', methods=['POST'])
def update_stock():
    try:
        data = request.get_json()
        print(f"Request data received: {data}")  # Debug line
        
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 0)
        operacion = data.get('operacion', 'incrementar')
        
        if not producto_id:
            return jsonify({'error': 'producto_id es requerido'}), 400
        
        print(f"Buscando producto con ID: {producto_id}, tipo: {type(producto_id)}")  # Debug
        
        # Intentar buscar por ID como string primero, luego como int
        productos_ref = db.collection('productos')
        
        # Buscar como string
        query = productos_ref.where('id', '==', str(producto_id)).limit(1)
        docs = list(query.stream())
        
        # Si no encuentra, buscar como int
        if not docs:
            print(f"No encontrado como string, buscando como int")
            try:
                query = productos_ref.where('id', '==', int(producto_id)).limit(1)
                docs = list(query.stream())
            except ValueError:
                pass
        
        if not docs:
            print(f"Producto no encontrado con ID: {producto_id}")
            return jsonify({'error': f'Producto no encontrado con ID: {producto_id}'}), 404
        
        doc = docs[0]
        producto_data = doc.to_dict()
        stock_actual = producto_data.get('stock_actual', 0)
        
        print(f"Producto encontrado: {producto_data}")
        print(f"Stock actual: {stock_actual}, Cantidad: {cantidad}, Operación: {operacion}")
        
        # Calcular nuevo stock
        if operacion == 'incrementar':
            nuevo_stock = stock_actual + cantidad
        elif operacion == 'decrementar':
            nuevo_stock = max(0, stock_actual - cantidad)  # No permitir stock negativo
        else:
            return jsonify({'error': 'Operación no válida'}), 400
        
        print(f"Nuevo stock calculado: {nuevo_stock}")
        
        # Actualizar el documento
        doc.reference.update({'stock_actual': nuevo_stock})
        
        print(f"Stock actualizado exitosamente")
        
        return jsonify({
            'message': 'Stock actualizado correctamente',
            'stock_anterior': stock_actual,
            'stock_nuevo': nuevo_stock,
            'producto_id': producto_id
        })
        
    except Exception as e:
        print(f"Error in update_stock: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/productos/<producto_id>/stock-absoluto', methods=['PUT'])
def set_stock_absoluto(producto_id):
    try:
        data = request.get_json()
        stock_absoluto = data.get('stock_absoluto', 0)
        
        # Buscar el producto
        productos_ref = db.collection('productos')
        query = productos_ref.where('id', '==', int(producto_id)).limit(1)
        docs = list(query.stream())
        
        if not docs:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        doc = docs[0]
        doc.reference.update({'stock_actual': stock_absoluto})
        
        return jsonify({
            'message': 'Stock establecido correctamente',
            'stock_nuevo': stock_absoluto
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/productos/<producto_id>', methods=['PUT'])
def update_producto(producto_id):
    try:
        data = request.get_json()
        
        # Buscar el producto
        productos_ref = db.collection('productos')
        query = productos_ref.where('id', '==', int(producto_id)).limit(1)
        docs = list(query.stream())
        
        if not docs:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        doc = docs[0]
        
        # Actualizar campos proporcionados
        update_data = {}
        if 'stock_actual' in data:
            update_data['stock_actual'] = data['stock_actual']
        if 'nombre' in data:
            update_data['nombre'] = data['nombre']
        if 'stock_minimo' in data:
            update_data['stock_minimo'] = data['stock_minimo']
        
        if update_data:
            doc.reference.update(update_data)
            return jsonify({'message': 'Producto actualizado correctamente'})
        else:
            return jsonify({'error': 'No hay datos para actualizar'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register-desperdicio', methods=['POST'])
def register_desperdicio():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('producto'):
            return jsonify({'error': 'Producto es requerido'}), 400
        if not data.get('cantidad') or data.get('cantidad') <= 0:
            return jsonify({'error': 'Cantidad debe ser mayor a 0'}), 400
        
        # Registrar el desperdicio
        desperdicio_data = {
            'producto': data.get('producto', ''),
            'producto_id': data.get('producto_id', ''),
            'cantidad': data.get('cantidad', 0),
            'motivo': data.get('motivo', ''),
            'descripcion': data.get('descripcion', ''),
            'timestamp': data.get('timestamp', ''),
            'operario': data.get('operario', ''),
            'tipo': 'desperdicio'
        }
        
        db.collection('desperdicios').add(desperdicio_data)
        
        return jsonify({'message': 'Desperdicio registrado correctamente'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-desperdicios', methods=['GET'])
def get_desperdicios():
    try:
        desperdicios = db.collection('desperdicios').stream()
        data = [doc.to_dict() for doc in desperdicios]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/set-stock-total', methods=['POST'])
def set_stock_total():
    try:
        data = request.get_json()
        producto_id = data.get('producto_id')
        cantidad_total = data.get('cantidad_total', 0)
        
        if not producto_id:
            return jsonify({'error': 'producto_id es requerido'}), 400
        
        # Buscar el producto
        productos_ref = db.collection('productos')
        query = productos_ref.where('id', '==', int(producto_id)).limit(1)
        docs = list(query.stream())
        
        if not docs:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        doc = docs[0]
        doc.reference.update({'stock_actual': cantidad_total})
        
        return jsonify({
            'message': 'Stock total establecido correctamente',
            'stock_nuevo': cantidad_total
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)