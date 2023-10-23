import xml.etree.ElementTree as Et
import json
from datetime import datetime


def get_users_by_date_range(start_date, end_date):
    try:
        tree = Et.parse('database/messages.xml')
        root = tree.getroot()

        users_by_date = {}  # Eliminamos el nivel "fechas"

        for message in root.findall('MENSAJE'):
            date_element = message.find('dd_mm_yyyy')

            if date_element is not None:
                date_str = date_element.text

                date = datetime.strptime(date_str, '%d/%m/%Y')

                if start_date <= date <= end_date:
                    users_element = message.find('USUARIOS')

                    if users_element is not None:
                        if date_str not in users_by_date:
                            users_by_date[date_str] = {}  # Almacenamos directamente bajo la fecha

                        for user in users_element.findall('USUARIO'):
                            username = user.text

                            if username in users_by_date[date_str]:
                                users_by_date[date_str][username] += 1
                            else:
                                users_by_date[date_str][username] = 1

        return json.dumps(users_by_date, indent=4, ensure_ascii=False)

    except FileNotFoundError:
        return json.dumps({'error': 'El archivo messages.xml no se encontró'}, indent=4, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'error': str(e)}, indent=4, ensure_ascii=False)


def get_hashtags_by_date_range(start_date, end_date):
    try:
        tree = Et.parse('database/messages.xml')
        root = tree.getroot()

        hashtags_by_date = {}  # Diccionario para almacenar datos de hashtags por fecha

        for message in root.findall('MENSAJE'):
            date_element = message.find('dd_mm_yyyy')

            if date_element is not None:
                date_str = date_element.text

                date = datetime.strptime(date_str, '%d/%m/%Y')

                if start_date <= date <= end_date:
                    hashtags_element = message.find('HASHTAGS')

                    if hashtags_element is not None:
                        for hashtag in hashtags_element.findall('HASHTAG'):
                            hashtag_text = hashtag.text

                            if date_str in hashtags_by_date:
                                if hashtag_text in hashtags_by_date[date_str]:
                                    hashtags_by_date[date_str][hashtag_text] += 1
                                else:
                                    hashtags_by_date[date_str][hashtag_text] = 1
                            else:
                                hashtags_by_date[date_str] = {hashtag_text: 1}

        return json.dumps(hashtags_by_date, indent=4, ensure_ascii=False)

    except FileNotFoundError:
        return {'error': 'El archivo messages.xml no se encontró'}
    except Exception as e:
        return {'error': str(e)}


def load_sentiment_dictionary(file_path):
    tree = Et.parse(file_path)
    root = tree.getroot()

    sentiment_dict = {
        "sentimientos_positivos": set(),
        "sentimientos_negativos": set(),
    }

    for elemento in root:
        for palabra in elemento:
            if elemento.tag == "sentimientos_negativos_rechazados":
                # Si es una etiqueta de sentimientos negativos rechazados, quitar la palabra del conjunto de negativos
                palabra_rechazada = palabra.text.lower()
                if palabra_rechazada in sentiment_dict["sentimientos_negativos"]:
                    sentiment_dict["sentimientos_negativos"].remove(palabra_rechazada)
            else:
                # Agregar palabras a los conjuntos de sentimientos positivos y negativos
                palabra_sentimiento = palabra.text.lower()
                sentiment_dict[elemento.tag].add(palabra_sentimiento)

    return sentiment_dict


def classify_messages(start_date, end_date, xml_file="database/messages.xml"):
    sentiment_dict = load_sentiment_dictionary('database/dictionary.xml')  # Carga el diccionario de sentimientos

    tree = Et.parse(xml_file)
    root = tree.getroot()

    results = {}  # Diccionario para almacenar los resultados

    for mensaje in root.findall("MENSAJE"):
        fecha_text = mensaje.find("dd_mm_yyyy").text
        fecha = datetime.strptime(fecha_text, '%d/%m/%Y')

        if start_date <= fecha <= end_date:
            texto = mensaje.find("TEXTO").text.lower()
            palabras = texto.split()
            positive_count = sum(1 for palabra in palabras if palabra in sentiment_dict["sentimientos_positivos"])
            negative_count = sum(1 for palabra in palabras if palabra in sentiment_dict["sentimientos_negativos"])

            if positive_count > negative_count:
                classification = "Positivo"
            elif positive_count < negative_count:
                classification = "Negativo"
            else:
                classification = "Neutro"

            fecha_str = fecha.strftime('%d/%m/%Y')

            if fecha_str not in results:
                results[fecha_str] = {
                    "Positivo": 0,
                    "Negativo": 0,
                    "Neutro": 0
                }

            results[fecha_str][classification] += 1

    return results


def clear_dictionary_db():
    try:
        tree = Et.parse("database/dictionary.xml")
        root = tree.getroot()

        # Recorre todas las palabras y elimínalas
        for sentiment in root:
            for word in sentiment.findall('palabra'):
                sentiment.remove(word)

        # Guarda el archivo XML actualizado
        tree.write("database/dictionary.xml", encoding='utf-8')
        return {'correct': 'Todas las palabras han sido eliminadas del diccionario.'}

    except FileNotFoundError:
        return {'error': 'El archivo no se encontró.'}
    except Exception as e:
        return {'error': str(e)}


def clear_messages_db():
    try:
        tree = Et.parse("database/messages.xml")
        root = tree.getroot()

        # Encuentra y elimina todos los elementos MENSAJE
        for mensaje in root.findall('MENSAJE'):
            root.remove(mensaje)

        # Guarda el archivo XML actualizado
        tree.write("database/messages.xml", encoding='utf-8')
        return {'correct': 'Todos los elementos MENSAJE han sido eliminados del archivo XML.'}

    except FileNotFoundError:
        return {'error': 'El archivo no se encontró.'}
    except Exception as e:
        return {'error': str(e)}


