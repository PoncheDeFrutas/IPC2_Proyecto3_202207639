from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from requests import post, get
from datetime import datetime
import json, os, base64
import xml.etree.ElementTree as Et
import json

def index(request):
    return render(request, 'index.html')


def reset_data(request):
    server_message = ""
    if request.method == 'POST':
        server_ip = settings.CLEAR_DATABASE
        response = post(server_ip)
        if response.status_code == 200:
            server_message = json.loads(response.text).get('Data')
        else:
            server_message = json.loads(response.text).get('Data')
    return render(request, 'reset_data.html', {'server_response_message': server_message})


def load_messages(request):
    return render(request, 'load_messages.html')


def load_dictionary(request):
    return render(request, 'load_dictionary.html')


def upload_file(request):
    server_message = ""
    source = ""
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        source = request.POST.get('source', '')
        server_ip = None

        if source == "load_messages":
            server_ip = settings.MESSAGES_SERVER_IP
        elif source == "load_dictionary":
            server_ip = settings.CONFIGURATIONS_SERVER_IP

        if server_ip:
            try:
                # Define el archivo y la clave específica
                files = {'my_custom_key': (uploaded_file.name, uploaded_file.read())}

                # Envía el archivo al servidor de destino
                response = post(server_ip, files=files)

                if response.status_code == 200:
                    server_message = xml_to_json(response.text)
                    server_message = json.loads(server_message)
                else:
                    server_message = "Error"

            except Exception as e:
                return HttpResponse('Error: ' + str(e))
        else:
            return HttpResponse('Fuente no válida.')
    return render(request, f'{source}.html', {'server_response_message': server_message})


def xml_to_json(xml_str):
    try:
        root = Et.fromstring(xml_str)
        xml_data = xml_to_dict(root)
        return json.dumps(xml_data)
    except Exception as e:
        return json.dumps({"error": str(e)})


def xml_to_dict(element):
    if len(element) == 0:
        return element.text
    result = {}
    for child in element:
        child_data = xml_to_dict(child)
        if child.tag in result:
            if type(result[child.tag]) is list:
                result[child.tag].append(child_data)
            else:
                result[child.tag] = [result[child.tag], child_data]
        else:
            result[child.tag] = child_data
    return result


def requests(request):
    action = request.GET.get('action')
    if action is not None:
        date_1 = request.GET.get('date_1')
        date_2 = request.GET.get('date_2')
        server_ip = None
        data_type = None

        # Formatea las fechas al formato "DD/MM/YYYY"
        date_1 = datetime.strptime(date_1, "%Y-%m-%d").strftime("%d/%m/%Y")
        date_2 = datetime.strptime(date_2, "%Y-%m-%d").strftime("%d/%m/%Y")
        params = {'date_1': date_1, 'date_2': date_2}

        if action == 'consultar-hashtags':
            server_ip = settings.RETURN_HASHTAGS
            data_type = 'hashtags'
        elif action == 'consultar-menciones':
            server_ip = settings.RETURN_USERS
            data_type = 'usuarios'
        elif action == 'consultar-sentimientos':
            server_ip = settings.RETURN_FEELINGS
            data_type = 'sentimientos'

        response = get(server_ip, params=params)

        # Verifica si la solicitud fue exitosa
        if response.status_code == 200:
            # Procesa la respuesta de Flask
            data_from_flask = response.json()  # Asume que Flask responde con JSON
            data_from_flask = {
                "data_type": data_type,
                "data": data_from_flask
            }
            return render(request, 'results.html', {'formatted_data': data_from_flask})
        else:
            # Maneja los errores, si es necesario
            return None  # O una respuesta de error adecuada

    return render(request, 'request.html')


def results(request):
    return render(request, 'results.html')


def graphics(request):
    return render(request, 'graphics.html')


def show_pdf(request):
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdf', "Manual_de_Usuario_Prueba_Funcional.pdf")

    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        return render(request, 'show_pdf.html', {'pdf_base64': pdf_base64})
    except FileNotFoundError:
        # Manejar el caso en el que el archivo no existe
        # Puedes mostrar un mensaje de error o redirigir a una página de error
        pass