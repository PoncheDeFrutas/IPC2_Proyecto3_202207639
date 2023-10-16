import re
import xml.etree.ElementTree as Et
from classes.Dictionary import Dictionary
from classes.Messages import Messages


class File_reading:
    def __init__(self, file_path):
        self.root = Et.parse(file_path).getroot()
        self.Dictionary = None
        self.Messages = []

    def get_messages(self):
        if not self.Messages:
            for message in self.root.findall('MENSAJE'):
                date = message.find('FECHA').text
                text = message.find('TEXTO').text
                users = []
                hashtags = []
                if date:
                    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date)
                    if match:
                        day = match.group(1).zfill(2)
                        month = match.group(2).zfill(2)
                        year = match.group(3)
                        date = f"{day}/{month}/{year}"
                if text:
                    users = re.findall(r'@[\w_]+', text)
                    hashtags = re.findall(r'#\w+#', text)
                self.Messages.append(Messages(date, text, users, hashtags))
            return self.Messages

    def get_dictionary(self, global_dictionary=Dictionary()):
        local_dictionary = global_dictionary
        if self.root.find('sentimientos_positivos').findall('palabra'):
            for positive_feeling in self.root.find('sentimientos_positivos').findall('palabra'):
                local_dictionary.add_feeling(positive_feeling.text, 'Positive')
        if self.root.find('sentimientos_negativos').findall('palabra'):
            for positive_feeling in self.root.find('sentimientos_negativos').findall('palabra'):
                local_dictionary.add_feeling(positive_feeling.text, 'Negative')
        return local_dictionary

def prueba():
    prueba = File_reading("../input_files/example_1.xml")
    for i in prueba.get_messages():
        print(i)

    prueba = File_reading("../input_files/feelings_1.xml")
    diccionario = prueba.get_dictionary()
    for i in prueba.get_dictionary().get_positive_feelings():
        print(i)

    prueba = File_reading("../input_files/feelings_2.xml")

    for i in prueba.get_dictionary(diccionario).get_positive_rejected():
        print(i)

prueba()