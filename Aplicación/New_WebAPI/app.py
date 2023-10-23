from flask_cors import CORS
from datetime import datetime
from flask import Flask, request, jsonify
from request.file_requests import *
from request.database_requests import *

app = Flask(__name__)

# Habilitar CORS
CORS(app)


# Ruta de bienvenida
@app.route('/')
def hello_world():
    return 'Hello World!'


# Ruta para procesar archivos XML
@app.route('/grabarMensajes', methods=['POST'])
def save_messages():
    try:
        files_json = process_xml_files()
        messages = extract_messages(files_json)
        response = save_messages_in_db(messages)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': f'Error al procesar los archivos XML---: {str(e)}'}), 500


@app.route('/grabarConfiguraciones', methods=['POST'])
def save_directory():
    try:
        response = save_dictionary_in_db(extract_feelings(process_xml_files()))
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': f'Error al procesar los archivos XML------: {str(e)}'}), 500


# Ruta para limpiar la base de datos
@app.route('/limpiarDatos', methods=['POST'])
def clear_database():
    # Implementa la lógica de limpiar la base de datos aquí
    clear_dictionary_db()
    clear_messages_db()
    return jsonify({"Data": "Base de datos reiniciada :D"})


# Función para manejar las rutas de devolución de datos (hashtags, menciones, sentimientos)
def return_data():
    date_one = request.args.get('date_1')
    date_two = request.args.get('date_2')

    if date_one is None or date_two is None:
        return {'error': 'Las fechas no se proporcionaron correctamente'}

    try:
        date_one = datetime.strptime(date_one, "%d/%m/%Y")
        date_two = datetime.strptime(date_two, "%d/%m/%Y")
    except ValueError:
        return {'error': 'El formato de fecha no es válido'}

    if date_one > date_two:
        return {'error': f"{date_one} es posterior a {date_two}"}
    elif date_one < date_two:
        return {'dates': [date_one, date_two]}
    else:
        return {'error': f"{date_one} es igual a {date_two}"}


# Rutas para devolver hashtags, menciones y sentimientos
@app.route('/devolverHashtags', methods=['GET'])
def return_hashtags():
    data = return_data()
    if 'error' in data:
        error_message = data['error']
        return jsonify({'error': error_message})
    else:
        correct_data = data['dates']
        response = get_hashtags_by_date_range(correct_data[0], correct_data[1])
        return response


@app.route('/devolverMenciones', methods=['GET'])
def return_mentions():
    data = return_data()

    if 'error' in data:
        error_message = data['error']
        return jsonify({'error': error_message})
    else:
        correct_data = data['dates']
        response = get_users_by_date_range(correct_data[0], correct_data[1])
        return response


@app.route('/devolverSentimientos', methods=['GET'])
def return_sentiments():
    data = return_data()

    if 'error' in data:
        error_message = data['error']
        return jsonify({'error': error_message})
    else:
        correct_data = data['dates']
        response = classify_messages(correct_data[0], correct_data[1])
        return response


@app.route('/devolverTodo', methods=['GET'])
def get_all():
    data = return_data()
    
    if 'error' in data:
        error_message = data['error']
        return jsonify({'error': error_message})

    correct_data = data['dates']
    
    # Obtener los resultados originales
    hashtags_data = json.loads(get_hashtags_by_date_range(correct_data[0], correct_data[1]))
    mentions_data = json.loads(get_users_by_date_range(correct_data[0], correct_data[1]))
    sentiments_data = classify_messages(correct_data[0], correct_data[1])

    # Procesar los resultados de hashtags para obtener la cantidad total
    total_hashtags = {}
    for date_data in hashtags_data.values():
        for hashtag, count in date_data.items():
            if hashtag in total_hashtags:
                total_hashtags[hashtag] += count
            else:
                total_hashtags[hashtag] = count

    # Procesar los resultados de menciones para obtener la cantidad total
    total_mentions = {}
    for date_data in mentions_data.values():
        for mention, count in date_data.items():
            if mention in total_mentions:
                total_mentions[mention] += count
            else:
                total_mentions[mention] = count

    # Procesar los resultados de sentimientos para obtener la cantidad total
    total_sentiments = {'Negativo': 0, 'Neutro': 0, 'Positivo': 0}
    for date_data in sentiments_data.values():
        for sentiment, count in date_data.items():
            total_sentiments[sentiment] += count

    return jsonify({'hashtags': total_hashtags, 'mentions': total_mentions, 'sentiments': total_sentiments})






if __name__ == '__main__':
    app.run()
