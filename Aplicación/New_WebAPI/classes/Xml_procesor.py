import json, xmltodict, re
from datetime import datetime
from unidecode import unidecode
import xml.dom.minidom as minidom
import xml.etree.ElementTree as Et

class Xml_procesor:
    def __init__(self):
        self.request = None
        self.response_data = []

    def process_xml_files(self, request, type_file):
        """
        Esta función procesa archivos XML enviados a través de una solicitud HTTP y los convierte en datos JSON.

        Args:
            request: La solicitud HTTP que contiene los archivos XML.

        Returns:
            list: Una lista que contiene datos JSON obtenidos a partir de los archivos XML procesados.

        """
        self.request = request
        self.response_data = []  # Lista para almacenar los datos JSON resultantes
        for key in self.request.files:
            xml_file = self.request.files[key]

            if xml_file and xml_file.filename.endswith('.xml'):
                xml_data = xml_file.read()  # Lee el contenido del archivo XML
                json_data = xmltodict.parse(xml_data)  # Convierte el contenido a formato JSON
                self.response_data.append(json_data)  # Agrega los datos JSON a la lista de respuesta
        if type_file == "messages":
            return self.save_messages_in_db(self.extract_messages())
        elif type_file == "feelings":
            return self.save_dictionary_in_db(self.extract_feelings())

    def extract_messages(self):
        """
        Esta función extrae mensajes de una lista de datos JSON. Los mensajes se buscan dentro de la estructura JSON
        utilizando la clave "MENSAJES".

        Returns:
            list: Una lista que contiene los mensajes extraídos. Cada mensaje es un diccionario.

        """
        messages = []
        for json_data in self.response_data:
            if "MENSAJES" in json_data:
                mensajes = json_data["MENSAJES"]["MENSAJE"]
                if isinstance(mensajes, list):
                    messages.extend(mensajes)
                elif isinstance(mensajes, dict):
                    messages.append(mensajes)
        return messages

    def extract_feelings(self):
        """
        Esta función extrae palabras asociadas con sentimientos positivos y negativos de una lista de datos JSON. Las palabras
        se buscan dentro de la estructura JSON utilizando las claves "diccionario", "sentimientos_positivos" y
        "sentimientos_negativos".

        Returns:
            list: Una lista que contiene las palabras asociadas con sentimientos positivos y negativos. Cada palabra se
                representa como un diccionario con un campo 'type' que indica si es positiva o negativa, y un campo 'data'
                que contiene la lista de palabras.

        """
        feelings = []
        for json_data in self.response_data:
            if "diccionario" in json_data:
                positive_feelings = json_data["diccionario"]["sentimientos_positivos"]["palabra"]
                negative_feelings = json_data["diccionario"]["sentimientos_negativos"]["palabra"]
                feelings.append({'type': "Positive", 'data': positive_feelings})
                feelings.append({'type': "Negative", 'data': negative_feelings})
        return feelings

    def format_xml(self, element):
        """
        Esta función formatea un elemento XML y sus elementos hijos, eliminando espacios en blanco innecesarios al principio y
        al final del texto de cada elemento.

        Args:
            element (Element): El elemento XML que se formateará.

        """
        for child in element:
            self.format_xml(child)

        if element.text:
            element.text = element.text.strip()
        if element.tail:
            element.tail = element.tail.strip()

    def save_messages_in_db(self, messages):
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
            summary_filename = 'database/resumenMensajes.xml'
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

            self.format_xml(root)

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

    def save_dictionary_in_db(self, feelings_list):
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
                    feeling = unidecode(feeling)
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
            self.format_xml(root)

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

            with open('database/resumenConfig.xml', 'w', encoding='utf-8') as xml_file:
                xml_file.write(xml_pretty)

            return xml_pretty
        except Exception as e:
            return {'error': f"Error al agregar sentimientos: {str(e)}"}