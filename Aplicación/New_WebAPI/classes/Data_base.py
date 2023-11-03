import xml.etree.ElementTree as Et
from datetime import datetime


class Data_base:
    def __init__(self):
        self.date_1 = None
        self.date_2 = None
        self.data_type = None
        self.sentiment_dict = None
        self.root = None

    def set_dates(self, date_1, date_2):
        self.date_1 = date_1
        self.date_2 = date_2

    def process_data(self, data_type):
        self.data_type = data_type
        data_base = "database/messages.xml"
        self.sentiment_dictionary()
        try:
            tree = Et.parse(f"{data_base}")
            self.root = tree.getroot()
            if data_type == "SENTIMIENTOS":
                return self.get_feelings_by_date()
            return self.get_data_by_date()
        except Exception as e:
            print(e)

    def get_data_by_date(self):
        try:
            data_by_date = {}

            for message in self.root.findall('MENSAJE'):
                date_element = message.find('dd_mm_yyyy')

                if date_element is not None:
                    date_str = date_element.text

                    date = datetime.strptime(date_str, '%d/%m/%Y')

                    if self.date_1 <= date <= self.date_2:
                        data_element = message.find(self.data_type)

                        if data_element is not None:
                            for user in data_element.findall(self.data_type[:-1]):
                                data = user.text

                                if date_str in data_by_date:
                                    if data in data_by_date[date_str]:
                                        data_by_date[date_str][data] += 1
                                    else:
                                        data_by_date[date_str][data] = 1
                                else:
                                    data_by_date[date_str] = {data: 1}

            return data_by_date  # Devuelve un diccionario en lugar de una cadena JSON
        except FileNotFoundError:
            return {'error': 'El archivo messages.xml no se encontró'}
        except Exception as e:
            return {'error': str(e)}

    def sentiment_dictionary(self):
        tree = Et.parse("database/dictionary.xml")
        self.root = tree.getroot()

        sentiment_dict = {
            "sentimientos_positivos": set(),
            "sentimientos_negativos": set(),
        }

        for elemento in self.root:
            for palabra in elemento:
                # Agregar palabras a los conjuntos de sentimientos positivos y negativos
                palabra_sentimiento = palabra.text.lower()
                if elemento.tag == "sentimientos_positivos":
                    sentiment_dict["sentimientos_positivos"].add(palabra_sentimiento)
                elif elemento.tag == "sentimientos_negativos":
                    sentiment_dict["sentimientos_negativos"].add(palabra_sentimiento)

        self.sentiment_dict = sentiment_dict

    def get_feelings_by_date(self):
        try:
            results = {}
            for mensaje in self.root.findall("MENSAJE"):
                fecha_text = mensaje.find("dd_mm_yyyy").text
                fecha = datetime.strptime(fecha_text, '%d/%m/%Y')

                if self.date_1 <= fecha <= self.date_2:
                    texto = mensaje.find("TEXTO").text.lower()
                    palabras = texto.split()
                    positive_count = sum(
                        1 for palabra in palabras if palabra in self.sentiment_dict["sentimientos_positivos"])
                    negative_count = sum(
                        1 for palabra in palabras if palabra in self.sentiment_dict["sentimientos_negativos"])

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
        except FileNotFoundError:
            return {'error': 'El archivo messages.xml no se encontró'}
        except Exception as e:
            return {'error': str(e)}

    def clear_dictionary_db(self):
        try:
            tree = Et.parse("database/dictionary.xml")
            self.root = tree.getroot()

            # Recorre todas las palabras y elimínalas
            for sentiment in self.root:
                for word in sentiment.findall('palabra'):
                    sentiment.remove(word)

            # Guarda el archivo XML actualizado
            tree.write("database/dictionary.xml", encoding='utf-8')
            return {'correct': 'Todas las palabras han sido eliminadas del diccionario.'}

        except FileNotFoundError:
            return {'error': 'El archivo no se encontró.'}
        except Exception as e:
            return {'error': str(e)}

    def clear_messages_db(self):
        """
        Esta función elimina todos los elementos de tipo 'MENSAJE' en un archivo XML.

        Returns:
            dict: Un diccionario con un mensaje de éxito si todos los elementos se eliminaron correctamente,
                o un mensaje de error si se encuentra un problema.

        """
        try:
            tree = Et.parse("database/messages.xml")
            self.root = tree.getroot()

            # Encuentra y elimina todos los elementos MENSAJE
            for mensaje in self.root.findall('MENSAJE'):
                self.root.remove(mensaje)

            # Guarda el archivo XML actualizado
            tree.write("database/messages.xml", encoding='utf-8')
            return {'correct': 'Todos los elementos MENSAJE han sido eliminados del archivo XML.'}

        except FileNotFoundError:
            return {'error': 'El archivo no se encontró.'}
        except Exception as e:
            return {'error': str(e)}

    def clear_all(self):
        self.clear_dictionary_db()
        self.clear_messages_db()
        return