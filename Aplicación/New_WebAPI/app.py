from flask_cors import CORS
from flask import Flask, request, jsonify, Response
from classes import *

app = Flask(__name__)

db_procesor = Date_procesor.Data_procesor()
xml_procesor = Xml_procesor.Xml_procesor()

# Habilitar CORS
CORS(app)

# Ruta de bienvenida (Prueba del Sistema)
@app.route('/')
def hello_world():
    return 'Hello World!'


# Ruta para grabar los mensajes
@app.route('/grabarMensajes', methods=['POST'])
def save_messages():
    try:
        global xml_procesor
        response = xml_procesor.process_xml_files(request, "messages")
        # Respuesta HTTP con el contenido XML y la cabecera Content-Type
        return Response(response, content_type='application/xml')

    except Exception as e:
        return jsonify({'error': f'Error al procesar los archivos XML: {str(e)}'}), 500


# Ruta para grabar las configuraciones
@app.route('/grabarConfiguraciones', methods=['POST'])
def save_directory():
    try:
        global xml_procesor
        response = xml_procesor.process_xml_files(request, "feelings")
        # Respuesta HTTP con el contenido XML y la cabecera Content-Type
        return Response(response, content_type='application/xml')
    except Exception as e:
        return jsonify({'error': f'Error al procesar los archivos XML------: {str(e)}'}), 500


# Ruta para limpiar la base de datos
@app.route('/limpiarDatos', methods=['POST'])
def clear_database():
    """
    Esta función es una vista que maneja las solicitudes POST en la ruta '/limpiarDatos'.
    Se encarga de limpiar o reiniciar las bases de datos de configuraciones de sentimientos y mensajes.
    Luego, devuelve una respuesta JSON que indica que la base de datos ha sido reiniciada.

    Returns:
        dict: Un diccionario JSON que indica que la base de datos ha sido reiniciada.

    """
    global db_procesor
    db_procesor.clear_db()
    return jsonify({"Data": "Base de datos reiniciada :D"})


# Ruta para devolver hashtags
@app.route('/devolverHashtags', methods=['GET'])
def return_hashtags():
    global db_procesor
    return jsonify(db_procesor.get_hashtags(request))


# Ruta para devolver menciones
@app.route('/devolverMenciones', methods=['GET'])
def return_mentions():
    global db_procesor
    return jsonify(db_procesor.get_mencions(request))


# Ruta para devolver sentimientos
@app.route('/devolverSentimientos', methods=['GET'])
def return_sentiments():
    global db_procesor
    return jsonify(db_procesor.get_feelings(request))


if __name__ == '__main__':
    app.run()

