import json, xmltodict, re
from flask import request, g
from datetime import datetime
from unidecode import unidecode
import xml.etree.ElementTree as Et
import xml.dom.minidom as minidom
from collections import defaultdict


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
    return feelings


def save_messages_in_db(messages):
    try:
        # Crear un nuevo archivo XML para el resumen de mensajes
        summary_root = Et.Element('MENSAJES_RECIBIDOS')
        tree_summary = Et.ElementTree(summary_root)

        for message in messages:
            obj_message = Et.Element("TIEMPO")

            date = message["FECHA"]

            date_element = Et.Element("FECHA")
            date_element.text = date

            msj_recibidos_element = Et.Element("MSJ_RECIBIDOS")
            msj_recibidos_element.text = "1"

            users_set = set()  # Conjunto para evitar usuarios duplicados
            for user in re.findall(r'@[\w_]+', message["TEXTO"].lower()):
                user = user.lower()  # Convierte el usuario a minúsculas
                users_set.add(user)

            usr_mencionados_element = Et.Element("USR_MENCIONADOS")
            usr_mencionados_element.text = str(len(users_set))

            hashtags_set = set()  # Conjunto para evitar hashtags duplicados
            for hashtag in re.findall(r'#\w+#', message["TEXTO"].lower()):
                hashtags_set.add(hashtag)

            hash_incluidos_element = Et.Element("HASH_INCLUIDOS")
            hash_incluidos_element.text = str(len(hashtags_set))

            obj_message.append(date_element)
            obj_message.append(msj_recibidos_element)
            obj_message.append(usr_mencionados_element)
            obj_message.append(hash_incluidos_element)

            summary_root.append(obj_message)

        # Formatear el XML del resumen antes de guardarlo
        xml_summary_string = Et.tostring(summary_root, encoding='utf-8')
        xml_summary_pretty = minidom.parseString(xml_summary_string).toprettyxml(indent='    ')

        # Guardar el resumen en un nuevo archivo XML
        summary_filename = 'database/summary.xml'
        with open(summary_filename, 'w', encoding='utf-8') as summary_file:
            summary_file.write(xml_summary_pretty)

        try:
            # Ahora, actualizar la base de datos original (messages.xml) con los mensajes nuevos
            tree = Et.parse('database/messages.xml')
            root = tree.getroot()
        except FileNotFoundError:
            root = Et.Element('MENSAJES')
            tree = Et.ElementTree(root)

        for message in messages:
            obj_message = Et.Element("MENSAJE")

            date = message["FECHA"]

            date_element = Et.Element("FECHA")
            date_element.text = date

            dd_mm_yyyy_element = Et.Element("dd_mm_yyyy")

            if date:
                match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date)
                if match:
                    day = match.group(1).zfill(2)
                    month = match.group(2).zfill(2)
                    year = match.group(3)

                    dd_mm_yyyy_element.text = f"{day}/{month}/{year}"

            text = message["TEXTO"]
            text_unidecode = unidecode(text.lower())

            text_element = Et.Element("TEXTO")
            text_element.text = text_unidecode

            users_element = Et.Element("USUARIOS")
            users_set = set()  # Conjunto para evitar usuarios duplicados

            for user in re.findall(r'@[\w_]+', text_unidecode):
                user = user.lower()  # Convierte el usuario a minúsculas
                if user not in users_set:
                    user_element = Et.Element('USUARIO')
                    user_element.text = user
                    users_element.append(user_element)
                    users_set.add(user)

            hashtags_element = Et.Element("HASHTAGS")
            hashtags_set = set()  # Conjunto para evitar hashtags duplicados

            for hashtag in re.findall(r'#\w+#', text_unidecode):
                if hashtag not in hashtags_set:
                    hashtag_element = Et.Element("HASHTAG")
                    hashtag_element.text = hashtag
                    hashtags_element.append(hashtag_element)
                    hashtags_set.add(hashtag)

            obj_message.append(date_element)
            obj_message.append(dd_mm_yyyy_element)
            obj_message.append(text_element)
            obj_message.append(users_element)
            obj_message.append(hashtags_element)

            root.append(obj_message)

        format_xml(root)

        # Formatear el XML original antes de guardarlo
        xml_string = Et.tostring(root, encoding='utf-8')
        xml_pretty = minidom.parseString(xml_string).toprettyxml(indent='    ')

        with open('database/messages.xml', 'w', encoding='utf-8') as xml_file:
            xml_file.write(xml_pretty)
        
        tree = Et.parse('database/messages.xml')
        root = tree.getroot()

        # Ordenar los elementos <MENSAJE> por la etiqueta <dd_mm_yyyy>
        root[:] = sorted(root, key=lambda mensaje: datetime.strptime(mensaje.find('dd_mm_yyyy').text, '%d/%m/%Y'))

        # Guardar el archivo XML ordenado
        tree.write('database/messages.xml')

        return xml_summary_pretty
    except json.JSONDecodeError as e:
        return {'error': f"Error al analizar el JSON: {e}"}


def order_messages_by_date(filename):
    # Parsea el archivo XML
    tree = Et.parse(filename)
    root = tree.getroot()

    # Obtiene todos los elementos MENSAJE
    messages = root.findall("MENSAJE")

    # Ordena los elementos MENSAJE por la fecha "dd_mm_yyyy"
    messages.sort(key=lambda message: message.find("dd_mm_yyyy").text)

    # Crea un nuevo árbol XML ordenado
    sorted_root = Et.Element("MENSAJES")
    sorted_tree = Et.ElementTree(sorted_root)

    # Agrega los elementos MENSAJE ordenados al nuevo árbol XML
    for message in messages:
        sorted_root.append(message)

    # Guarda el árbol XML ordenado en un nuevo archivo
    sorted_filename = "ordered_messages.xml"
    sorted_tree.write(sorted_filename, encoding="utf-8", xml_declaration=True)


def format_xml(element):
    for child in element:
        format_xml(child)

    if element.text:
        element.text = element.text.strip()
    if element.tail:
        element.tail = element.tail.strip()


def save_dictionary_in_db(feelings_list):
    try:
        try:
            tree = Et.parse('database/dictionary.xml')
            root = tree.getroot()
        except FileNotFoundError:
            root = Et.Element('diccionario')
            tree = Et.ElementTree(root)

        word_count = {
            'sentimientos_positivos': 0,
            'sentimientos_negativos': 0,
            'sentimientos_negativos_rechazados': 0,
            'sentimientos_positivo_rechazados': 0
        }

        for feeling_data in feelings_list:
            type_feeling = feeling_data["type"]
            feelings = feeling_data["data"]

            table_feeling_name_principal = ""
            table_feeling_name_secondary = ""
            table_rejected_name = ""

            if type_feeling == "Positive":
                table_feeling_name_principal = "sentimientos_positivos"
                table_feeling_name_secondary = "sentimientos_negativos"
                table_rejected_name = "sentimientos_positivo_rechazados"
            elif type_feeling == "Negative":
                table_feeling_name_principal = "sentimientos_negativos"
                table_feeling_name_secondary = "sentimientos_positivos"
                table_rejected_name = "sentimientos_negativos_rechazados"
            else:
                continue

            type_feeling_element_principal = root.find(table_feeling_name_principal)
            if type_feeling_element_principal is None:
                type_feeling_element_principal = Et.Element(table_feeling_name_principal)
                root.append(type_feeling_element_principal)

            type_feeling_element_secondary = root.find(table_feeling_name_secondary)
            if type_feeling_element_secondary is None:
                type_feeling_element_secondary = Et.Element(table_feeling_name_secondary)
                root.append(type_feeling_element_secondary)

            type_feeling_element_rejected = root.find(table_rejected_name)
            if type_feeling_element_rejected is None:
                type_feeling_element_rejected = Et.Element(table_rejected_name)
                root.append(type_feeling_element_rejected)

            for feeling in feelings:
                feeling_element_principal = type_feeling_element_principal.find(f"palabra[.='{feeling}']")
                feeling_element_secondary = type_feeling_element_secondary.find(f"palabra[.='{feeling}']")
                feeling_element_rejected = type_feeling_element_rejected.find(f"palabra[.='{feeling}']")
                new_feeling = Et.Element('palabra')
                new_feeling.text = feeling
                if feeling_element_principal is None and feeling_element_secondary is None:
                    type_feeling_element_principal.append(new_feeling)
                    word_count[table_feeling_name_principal] += 1
                elif feeling_element_secondary is not None and feeling_element_rejected is None:
                    type_feeling_element_rejected.append(new_feeling)
                    word_count[table_rejected_name] += 1

        # Eliminar espacios en blanco y saltos de línea innecesarios
        format_xml(root)

        # Formatear el XML antes de guardarlo
        xml_string = Et.tostring(root, encoding='utf-8')
        xml_pretty = minidom.parseString(xml_string).toprettyxml(indent='    ')

        with open('database/dictionary.xml', 'w', encoding='utf-8') as xml_file:
            xml_file.write(xml_pretty)

        config_recibida = Et.Element("CONFIG_RECIBIDA")

        palabras_positivas = Et.SubElement(config_recibida, "PALABRAS_POSITIVAS")
        palabras_positivas.text = str(word_count["sentimientos_positivos"])

        palabras_positivas_rechazada = Et.SubElement(config_recibida, "PALABRAS_POSITIVAS_RECHAZADA")
        palabras_positivas_rechazada.text = str(word_count["sentimientos_positivo_rechazados"])

        palabras_negativas = Et.SubElement(config_recibida, "PALABRAS_NEGATIVAS")
        palabras_negativas.text = str(word_count["sentimientos_negativos"])

        palabras_negativas_rechazada = Et.SubElement(config_recibida, "PALABRAS_NEGATIVAS_RECHAZADA")
        palabras_negativas_rechazada.text = str(word_count["sentimientos_negativos_rechazados"])

        xml_output = Et.tostring(config_recibida, encoding="utf-8")
        xml_pretty = minidom.parseString(xml_output).toprettyxml(indent='    ')

        return xml_pretty
    except Exception as e:
        return {'error': f"Error al agregar sentimientos: {str(e)}"}
    except json.JSONDecodeError as e:
        return {'error': f"Error al analizar el JSON: {e}"}
