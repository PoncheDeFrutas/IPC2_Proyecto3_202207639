from flask_cors import CORS
from datetime import datetime
from flask import Flask, jsonify, request
from requests_.database_requests import initialize_db, clear_db, get_elements_between_dates, get_hashtags_count_by_date
from requests_.database_requests import get_users_count_by_date, get_feelins_count_by_date
from requests_.files_requests import process_xml_files, extract_messages, save_messages, extract_feelings

app = Flask(__name__)
CORS(app)
app.config['DATABASE'] = 'database.db'


@app.route('/')
def init():
    return "nice"


@app.route('/grabarMensajes', methods=['POST'])
def record_messages():
    try:
        response_data = process_xml_files()
        messages = extract_messages(response_data)
        response = save_messages(messages)
        return response
    except Exception as e:
        return jsonify({'error': f'Error al procesar los archivos XML: {str(e)}'}), 500


@app.route('/grabarConfiguracion', methods=['POST'])
def record_config():
    try:
        response_data = process_xml_files()
        response = extract_feelings(response_data)
        return response
    except Exception as e:
        return jsonify({'error': f'Error al procesar los archivos XML: {str(e)}'}), 500


@app.route('/limpiarDatos', methods=['POST'])
def clear_database():
    clear_db()
    return 'Base de datos limpia'


@app.route('/devolerHashtags', methods=['POST'])
def post_return_hashtags():
    pass


@app.route('/devolerHashtags', methods=['GET'])
def get_return_hashtags():
    date_one = datetime.strptime(request.args.get('date_1'), "%d/%m/%Y")
    date_two = datetime.strptime(request.args.get('date_2'), "%d/%m/%Y")
    if date_one > date_two:
        print(f"{date_one} es posterior a {date_two}")
    elif date_one < date_two:
        response = get_elements_between_dates(date_one, date_two)
        return get_hashtags_count_by_date(response)
    else:
        print(f"{date_one} es igual a {date_two}")


@app.route('/devolerMenciones', methods=['POST'])
def post_return_mencions():
    pass


@app.route('/devolerMenciones', methods=['GET'])
def get_return_mencions():
    date_one = datetime.strptime(request.args.get('date_1'), "%d/%m/%Y")
    date_two = datetime.strptime(request.args.get('date_2'), "%d/%m/%Y")
    if date_one > date_two:
        print(f"{date_one} es posterior a {date_two}")
    elif date_one < date_two:
        response = get_elements_between_dates(date_one, date_two)
        return get_users_count_by_date(response)
    else:
        print(f"{date_one} es igual a {date_two}")


@app.route('/devolverSentimientos', methods=['POST'])
def post_return_feelings():
    pass


@app.route('/devolverSentimientos', methods=['GET'])
def get_return_feelings():
    date_one = datetime.strptime(request.args.get('date_1'), "%d/%m/%Y")
    date_two = datetime.strptime(request.args.get('date_2'), "%d/%m/%Y")
    if date_one > date_two:
        print(f"{date_one} es posterior a {date_two}")
    elif date_one < date_two:
        response = get_elements_between_dates(date_one, date_two)
        return get_feelins_count_by_date(response)
    else:
        print(f"{date_one} es igual a {date_two}")


@app.route('/initialize_db', methods=['POST'])
def initialize_database():
    initialize_db()
    return 'Base de datos inicializada'


if __name__ == '__main':
    app.run(debug=True, port=3050)