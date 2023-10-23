 import json
import xmltodict, re
from flask import request, g
from datetime import datetime
from unidecode import unidecode
from requests_.database_requests import get_db
import xml.etree.ElementTree as Et


def process_xml_files():
    response_data = []
    for key in request.files:
        xml_file = request.files[key]

        if xml_file and xml_file.filename.endswith('.xml'):
            xml_data = xml_file.read()
            json_data = xmltodict.parse(xml_data)
            response_data.append(json_data)
    return response_data


def extract_messages(response_data):
    messages = []
    for json_data in response_data:
        if "MENSAJES" in json_data:
            mensajes = json_data["MENSAJES"]["MENSAJE"]
            if isinstance(mensajes, list):
                messages.extend(mensajes)
            elif isinstance(mensajes, dict):
                messages.append(mensajes)
    return messages


def extract_feelings(response_data):
    feelings = []
    for json_data in response_data:
        if "diccionario" in json_data:
            positive_feelings = json_data["diccionario"]["sentimientos_positivos"]["palabra"]
            negative_feelings = json_data["diccionario"]["sentimientos_negativos"]["palabra"]
            feelings.append({'type': "Positive", 'data': positive_feelings})
            feelings.append({'type': "Negative", 'data': negative_feelings})
    return save_dictionary(feelings)


def save_messages(messages):
    try:
        db = get_db()
        cursor = db.cursor()

        # Crear un elemento raíz para el XML
        root = Et.Element("messages")

        for message in messages:
            date = message["FECHA"]
            text = message["TEXTO"]
            text_unidecode = unidecode(text.lower())
            users = re.findall(r'@[\w_]+', text_unidecode)
            hashtags = re.findall(r'#\w+#', text_unidecode)
            dd_mm_yyyy = ""

            if date:
                match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date)
                if match:
                    day = match.group(1).zfill(2)
                    month = match.group(2).zfill(2)
                    year = match.group(3)
                    dd_mm_yyyy = f"{day}/{month}/{year}"

            # Insertar en la base de datos
            cursor.execute("INSERT INTO messages (date_, text, dd_mm_yyyy) VALUES (?, ?, ?)",
                           (date, text_unidecode, datetime.strptime(dd_mm_yyyy, "%d/%m/%Y")))

            message_id = cursor.lastrowid  # Obtener el ID del mensaje recién insertado

            # Insertar usuarios en la tabla "users" y relacionarlos con el mensaje si no existen
            for user in users:
                cursor.execute("SELECT id FROM users WHERE users = ?", (user,))
                user_row = cursor.fetchone()
                if user_row:
                    user_id = user_row[0]
                else:
                    cursor.execute("INSERT INTO users (users) VALUES (?)", (user,))
                    user_id = cursor.lastrowid  # Obtener el ID del usuario recién insertado
                cursor.execute("INSERT INTO messages_users (message_id, user_id) VALUES (?, ?)",
                               (message_id, user_id))

            # Insertar hashtags en la tabla "hashtags" y relacionarlos con el mensaje si no existen
            for hashtag in hashtags:
                cursor.execute("SELECT id FROM hashtags WHERE hashtags = ?", (hashtag,))
                hashtag_row = cursor.fetchone()
                if hashtag_row:
                    hashtag_id = hashtag_row[0]
                else:
                    cursor.execute("INSERT INTO hashtags (hashtags) VALUES (?)", (hashtag,))
                    hashtag_id = cursor.lastrowid  # Obtener el ID del hashtag recién insertado
                cursor.execute("INSERT INTO messages_hashtags (message_id, hashtag_id) VALUES (?, ?)",
                               (message_id, hashtag_id))

            # Crear elementos XML para el mensaje actual
            message_element = Et.Element("message")
            root.append(message_element)

            date_element = Et.Element("date")
            date_element.text = date
            message_element.append(date_element)

            text_element = Et.Element("text")
            text_element.text = text_unidecode
            message_element.append(text_element)

            dd_mm_yyyy_element = Et.Element("dd_mm_yyyy")
            dd_mm_yyyy_element.text = dd_mm_yyyy
            message_element.append(dd_mm_yyyy_element)

            users_element = Et.Element("users")
            for user in users:
                user_element = Et.Element("user")
                user_element.text = user
                users_element.append(user_element)
            message_element.append(users_element)

            hashtags_element = Et.Element("hashtags")
            for hashtag in hashtags:
                hashtag_element = Et.Element("hashtag")
                hashtag_element.text = hashtag
                hashtags_element.append(hashtag_element)
            message_element.append(hashtags_element)

        # Convertir la estructura XML en una cadena de texto
        xml_response = Et.tostring(root, encoding="utf-8").decode()

        # Realizar la operación de commit en la base de datos y cerrar la conexión
        db.commit()
        db.close()

        return xml_response
    except json.JSONDecodeError as e:
        print(f"Error al analizar el JSON: {e}")
        return None


def save_dictionary(feelings_list):
    try:
        db = get_db()
        cursor = db.cursor()
        for feeling_data in feelings_list:
            type_feeling = feeling_data["type"]
            feelings = feeling_data["data"]
            if type_feeling == "Positive":
                table_feeling_name_principal = "positive_feelings"
                table_feeling_name_secondary = "negative_feelings"
                table_rejected_name = "negative_rejected"
            elif type_feeling == "Negative":
                table_feeling_name_principal = "negative_feelings"
                table_feeling_name_secondary = "positive_feelings"
                table_rejected_name = "positive_rejected"
            else:
                continue

            for feeling in feelings:
                cursor.execute(f"SELECT id FROM {table_feeling_name_principal} WHERE feeling = ?", (unidecode(feeling.lower()),))
                result_1 = cursor.fetchone()
                cursor.execute(f"SELECT id FROM {table_feeling_name_secondary} WHERE feeling = ?", (unidecode(feeling.lower()),))
                result_2 = cursor.fetchone()
                cursor.execute(f"SELECT id FROM {table_rejected_name} WHERE feeling = ?", (unidecode(feeling.lower()),))
                result_3 = cursor.fetchone()

                if result_1 is None and result_2 is None:
                    cursor.execute(f"INSERT INTO {table_feeling_name_principal} (feeling) VALUES(?)", (unidecode(feeling.lower()),))
                elif result_2 is not None and result_3 is None:
                    cursor.execute(f"INSERT INTO {table_rejected_name} (feeling) VALUES(?)", (unidecode(feeling.lower()),))

        db.commit()

        # Generar el XML
        root = Et.Element("diccionario")

        positive_sentiments_element = Et.Element("sentimientos_positivos")
        negative_sentiments_element = Et.Element("sentimientos_negativos")
        positive_rejected_sentiments_element = Et.Element("positivos_rechazados")
        negative_rejected_sentiments_element = Et.Element("negativos_rechazados")

        root.append(positive_sentiments_element)
        root.append(negative_sentiments_element)
        root.append(positive_rejected_sentiments_element)
        root.append(negative_rejected_sentiments_element)

        cursor.execute(f"SELECT feeling FROM positive_feelings")
        positive_feelings = [row[0] for row in cursor.fetchall()]
        cursor.execute(f"SELECT feeling FROM negative_feelings")
        negative_feelings = [row[0] for row in cursor.fetchall()]
        cursor.execute(f"SELECT feeling FROM positive_rejected")
        positive_rejected = [row[0] for row in cursor.fetchall()]
        cursor.execute(f"SELECT feeling FROM negative_rejected")
        negative_rejected = [row[0] for row in cursor.fetchall()]

        for feeling in positive_feelings:
            feeling_element = Et.Element("palabra")
            feeling_element.text = feeling
            positive_sentiments_element.append(feeling_element)

        for feeling in negative_feelings:
            feeling_element = Et.Element("palabra")
            feeling_element.text = feeling
            negative_sentiments_element.append(feeling_element)

        for feeling in positive_rejected:
            feeling_element = Et.Element("palabra")
            feeling_element.text = feeling
            positive_rejected_sentiments_element.append(feeling_element)

        for feeling in negative_rejected:
            feeling_element = Et.Element("palabra")
            feeling_element.text = feeling
            negative_rejected_sentiments_element.append(feeling_element)

        xml_response = Et.tostring(root, encoding="utf-8")
        db.close()
        return xml_response.decode("utf-8")
    except Exception as e:
        # Manejo general de otras excepciones
        print("Ocurrió una excepción:", str(e))
        return None