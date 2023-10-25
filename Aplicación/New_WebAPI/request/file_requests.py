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
        try:
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
            for user in re.findall(r'@[\w_]+', text_unidecode):
                user_element = Et.Element('USUARIO')
                user_element.text = user
                users_element.append(user_element)

            hashtags_element = Et.Element("HASHTAGS")
            for hashtag in re.findall(r'#\w+#', text_unidecode):
                hashtag_element = Et.Element("HASHTAG")
                hashtag_element.text = hashtag
                hashtags_element.append(hashtag_element)

            obj_message.append(date_element)
            obj_message.append(dd_mm_yyyy_element)
            obj_message.append(text_element)
            obj_message.append(users_element)
            obj_message.append(hashtags_element)

            root.append(obj_message)

        format_xml(root)

        # Formatear el XML antes de guardarlo
        xml_string = Et.tostring(root, encoding='utf-8')
        xml_pretty = minidom.parseString(xml_string).toprettyxml(indent='    ')

        with open('database/messages.xml', 'w', encoding='utf-8') as xml_file:
            xml_file.write(xml_pretty)
        return {'correct': 'Mensajes Actualizados'}
    except json.JSONDecodeError as e:
        return {'error': f"Error al analizar el JSON: {e}"}


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

        for feeling_data in feelings_list:
            type_feeling = feeling_data["type"]
            feelings = feeling_data["data"]

            table_feeling_name_principal = ""
            table_feeling_name_secondary = ""
            table_rejected_name = ""

            if type_feeling == "Positive":
                table_feeling_name_principal = "sentimientos_positivos"
                table_feeling_name_secondary = "sentimientos_negativos"
                table_rejected_name = "sentimientos_negativos_rechazados"
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
                elif feeling_element_secondary is not None and feeling_element_rejected is None:
                    type_feeling_element_rejected.append(new_feeling)

        # Eliminar espacios en blanco y saltos de línea innecesarios
        format_xml(root)

        # Formatear el XML antes de guardarlo
        xml_string = Et.tostring(root, encoding='utf-8')
        xml_pretty = minidom.parseString(xml_string).toprettyxml(indent='    ')

        with open('database/dictionary.xml', 'w', encoding='utf-8') as xml_file:
            xml_file.write(xml_pretty)

        return {'correct': 'Sentimientos agregados al diccionario'}
    except Exception as e:
        return {'error': f"Error al agregar sentimientos: {str(e)}"}
    except json.JSONDecodeError as e:
        return {'error': f"Error al analizar el JSON: {e}"}


def generate_resume_config():
    try:
        tree = Et.parse("database/dictionary.xml")
        root = tree.getroot()

        positive_feelings = 0
        negative_feelings = 0
        positive_rejected = 0
        negative_rejected = 0

        for feeling in root:
            if feeling.tag == "sentimientos_positivos":
                positive_feelings = len(feeling)
            elif feeling.tag == "sentimientos_negativos":
                negative_feelings = len(feeling)
            elif feeling.tag ==  "sentimientos_negativos_rechazados":
                negative_rejected = len(feeling)
            elif feeling.tag == "sentimientos_positivos_rechazados":
                positive_rejected = len(feeling)
        
        config_element = Et.Element('CONFIG_RECIBIDA')
        Et.SubElement(config_element, 'PALABRAS_POSITIVAS').text = str(positive_feelings)
        Et.SubElement(config_element, 'PALABRAS_POSITIVAS_RECHAZADA').text = str(positive_rejected)
        Et.SubElement(config_element, 'PALABRAS_NEGATIVAS').text = str(negative_feelings)
        Et.SubElement(config_element, 'PALABRAS_NEGATIVAS_RECHAZADA').text = str(negative_rejected)


        xml_string = Et.tostring(config_element, encoding='utf-8')
        xml_pretty = minidom.parseString(xml_string).toprettyxml(indent='    ')

        # Guardar el nuevo archivo XML
        with open('database/resumenConfig.xml', 'w', encoding='utf-8') as xml_file:
            xml_file.write(xml_pretty)
        
        result = {'correct': xml_pretty}
    except Exception as e:
        result = {'error': str(e)}
    
    return result


def generate_resume_messages():
    try:
        # Parsea el XML de entrada
        tree = Et.parse("database/messages.xml")
        root = tree.getroot()

        # Estructura para almacenar el conteo de mensajes por fecha, usuarios y hashtags
        count_data = defaultdict(lambda: {'MSJ_RECIBIDOS': 0, 'USR_MENCIONADOS': set(), 'HASH_INCLUIDOS': set()})

        # Procesa cada mensaje
        for mensaje in root.findall('.//MENSAJE'):
            fecha = mensaje.find('dd_mm_yyyy').text
            usuarios = [usuario.text for usuario in mensaje.findall('.//USUARIO')]
            hashtags = [hashtag.text for hashtag in mensaje.findall('.//HASHTAG')]

            # Actualiza los conteos
            count_data[fecha]['MSJ_RECIBIDOS'] += 1
            count_data[fecha]['USR_MENCIONADOS'].update(usuarios)
            count_data[fecha]['HASH_INCLUIDOS'].update(hashtags)

        # Crea el nuevo XML con los datos de conteo
        result_root = Et.Element('MENSAJES_RECIBIDOS')

        for fecha, conteo in count_data.items():
            tiempo = Et.SubElement(result_root, 'TIEMPO')
            Et.SubElement(tiempo, 'FECHA').text = fecha
            Et.SubElement(tiempo, 'MSJ_RECIBIDOS').text = str(conteo['MSJ_RECIBIDOS'])
            Et.SubElement(tiempo, 'USR_MENCIONADOS').text = str(len(conteo['USR_MENCIONADOS']))
            Et.SubElement(tiempo, 'HASH_INCLUIDOS').text = str(len(conteo['HASH_INCLUIDOS']))

        # Genera el nuevo archivo XML
        result_tree = Et.ElementTree(result_root)
        xml_string = Et.tostring(result_root, encoding='utf-8')
        xml_pretty = minidom.parseString(xml_string).toprettyxml(indent='    ')

        with open("database/resumenMensajes.xml", 'w', encoding='utf-8') as xml_file:
            xml_file.write(xml_pretty)

        resultado = {'correct': xml_pretty}
    except Exception as e:
        resultado = {'error': str(e)}
    
    return resultado