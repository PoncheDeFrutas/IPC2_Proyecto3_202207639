import sqlite3
from datetime import datetime
from flask import g, current_app
import xml.etree.ElementTree as Et


def get_db():
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect(current_app.config['DATABASE'])
    return g.db


def get_elements_between_dates(date_1, date_2):
    db = get_db()
    cursor = db.cursor()
    consult = "SELECT * FROM messages WHERE dd_mm_yyyy BETWEEN ? AND ?"
    cursor.execute(consult, (date_1, date_2))
    result = cursor.fetchall()

    # Ordena los resultados por fecha
    result_sorted = sorted(result, key=lambda tupla: datetime.strptime(tupla[3], '%Y-%m-%d %H:%M:%S'))

    # Convierte los resultados ordenados en una lista
    ordered_dates = [tupla[3] for tupla in result_sorted]

    unique_list = []

    for item in ordered_dates:
        if item not in unique_list:
            unique_list.append(item)

    return unique_list


def get_hashtags_count_by_date(dates):
    db = get_db()
    cursor = db.cursor()

    # Create an element root for the XML
    root = Et.Element("hashtags_count")

    consult = """
        SELECT h.hashtags, COUNT(mh.message_id) AS veces_utilizado
        FROM messages_hashtags mh
        JOIN messages m ON mh.message_id = m.id
        JOIN hashtags h ON mh.hashtag_id = h.id
        WHERE m.dd_mm_yyyy = ?
        GROUP BY h.hashtags
        ORDER BY veces_utilizado DESC;
    """

    for date in dates:
        cursor.execute(consult, (date,))
        hashtags_data = cursor.fetchall()

        # Create an XML element for each date
        date_element = Et.Element("date")
        root.append(date_element)

        # Add the "date_time" element within the "date" element
        date_time_element = Et.Element("date_time")
        date_time_element.text = date
        date_element.append(date_time_element)

        # Add information about hashtags within the "date" element
        hashtags_element = Et.Element("hashtags")
        date_element.append(hashtags_element)

        for hashtag_data in hashtags_data:
            hashtag_entry = Et.Element("hashtag")
            hashtags_element.append(hashtag_entry)

            hashtag_text = Et.Element("text")
            hashtag_text.text = hashtag_data[0]
            hashtag_entry.append(hashtag_text)

            hashtag_count = Et.Element("count")
            hashtag_count.text = str(hashtag_data[1])
            hashtag_entry.append(hashtag_count)

    # Convert the XML structure into a string with UTF-8 encoding
    xml_response = Et.tostring(root, encoding="utf-8").decode()
    return xml_response


def get_users_count_by_date(dates):
    db = get_db()
    cursor = db.cursor()

    # Create an element root for the XML
    root = Et.Element("users_count")

    consult = """
        SELECT u.users, COUNT(mu.message_id) AS veces_utilizado
        FROM messages_users mu
        JOIN messages m ON mu.message_id = m.id
        JOIN users u ON mu.user_id = u.id
        WHERE m.dd_mm_yyyy = ?
        GROUP BY u.users
        ORDER BY veces_utilizado DESC;
    """

    for date in dates:
        cursor.execute(consult, (date,))
        users_data = cursor.fetchall()

        # Create an XML element for each date
        date_element = Et.Element("date")
        root.append(date_element)

        # Add the "date_time" element within the "date" element
        date_time_element = Et.Element("date_time")
        date_time_element.text = date
        date_element.append(date_time_element)

        # Add information about users
        users_element = Et.Element("users")
        date_element.append(users_element)

        for user_data in users_data:
            user_entry = Et.Element("user")
            users_element.append(user_entry)

            user_name = Et.Element("name")
            user_name.text = user_data[0]
            user_entry.append(user_name)

            user_count = Et.Element("count")
            user_count.text = str(user_data[1])
            user_entry.append(user_count)

    # Convert the XML structure into a string with UTF-8 encoding
    xml_response = Et.tostring(root, encoding="utf-8").decode()
    return xml_response


def get_feelins_count_by_date(dates):
    db = get_db()
    cursor = db.cursor()

    # Crear un elemento raíz para el XML
    root = Et.Element("feelings_count")

    # Crea un conjunto de sentimientos positivos y negativos para una búsqueda más eficiente
    consult = "SELECT feeling FROM positive_feelings"
    cursor.execute(consult)
    positive_feelings = set(row[0] for row in cursor.fetchall())

    consult = "SELECT feeling FROM negative_feelings"
    cursor.execute(consult)
    negative_feelings = set(row[0] for row in cursor.fetchall())

    for date in dates:
        consult = "SELECT text FROM messages WHERE dd_mm_yyyy = ?"
        cursor.execute(consult, (date,))
        messages = cursor.fetchall()

        positive_messages = 0
        negative_messages = 0
        neutral_messages = 0

        for message in messages:
            positive_count = 0
            negative_count = 0

            text = message[0].lower()
            for feeling in positive_feelings:
                if feeling in text:
                    positive_count += 1
            for feeling in negative_feelings:
                if feeling in text:
                    negative_count += 1

            if positive_count > negative_count:
                positive_messages += 1
            elif negative_count > positive_count:
                negative_messages += 1
            elif negative_count == positive_count:
                neutral_messages += 1

        # Crear un elemento XML para cada fecha
        date_element = Et.Element("date")
        root.append(date_element)

        # Agregar el formato de fecha y hora
        date_time_element = Et.Element("date_time")
        date_time_element.text = date
        date_element.append(date_time_element)

        # Agregar la cantidad de mensajes positivos, negativos y neutros
        positive_element = Et.Element("positive_messages")
        positive_element.text = str(positive_messages)
        date_element.append(positive_element)

        negative_element = Et.Element("negative_messages")
        negative_element.text = str(negative_messages)
        date_element.append(negative_element)

        neutral_element = Et.Element("neutral_messages")
        neutral_element.text = str(neutral_messages)
        date_element.append(neutral_element)

    # Convertir la estructura XML en una cadena de texto
    xml_response = Et.tostring(root, encoding="utf-8").decode()
    return xml_response


def drop_tables():
    db = get_db()
    cursor = db.cursor()

    tables = ["positive_feelings", "negative_feelings", "positive_rejected",
              "negative_rejected", "dictionary", "hashtags", "messages", "users", "messages_users", "messages_hashtags"]

    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    db.commit()


def init_db():
    with current_app.app_context():
        db = get_db()
        with current_app.open_resource('database/schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()


def initialize_db():
    init_db()


def clear_db():
    drop_tables()
    init_db()
