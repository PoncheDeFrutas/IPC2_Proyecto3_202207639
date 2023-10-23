from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from requests import post, get, exceptions


def index(request):
    url = "http://127.0.0.1:5000/"
    obj_template = loader.get_template("index.html")
    html = obj_template.render()
    return HttpResponse(html)


def is_xml_files(uploaded_files):
    # Verifica si el archivo tiene una extensión XML
    valid_files = []
    for file in uploaded_files:
        if file.name.lower().endswith('.xml'):
            valid_files.append(file)

    return valid_files


# Esta función puede ser utilizada para procesar tanto mensajes como diccionarios
def upload_data(request, endpoint):
    if request.method == 'POST':
        uploaded_files = ""
        if endpoint == 'grabarConfiguracion':
            uploaded_files = request.FILES.getlist('dictionary_archive')  # Cambiar el nombre del campo según corresponda
        elif endpoint == "grabarMensajes":
            uploaded_files = request.FILES.getlist('messages_archive')
        valid_files = is_xml_files(uploaded_files)

        if valid_files:
            url = f"http://127.0.0.1:5000/{endpoint}"

            # Crear un diccionario de archivos para ser enviados
            files = {f.name: f for f in valid_files}

            try:
                response = post(url, files=files)

                if response.status_code == 200:
                    # Procesa la respuesta del servidor remoto según sea necesario
                    # response.text contiene la respuesta del servidor
                    return HttpResponse('Archivos XML subidos con éxito.')
                else:
                    return HttpResponse('Error al subir los archivos XML al servidor remoto.')
            except exceptions.RequestException as e:
                return HttpResponse(f'Error al enviar los archivos XML: {str(e)}')

        else:
            return HttpResponse('No se encontraron archivos XML válidos para subir.')


@csrf_exempt
def save_messages(request):
    return upload_data(request, "grabarMensajes")


@csrf_exempt
def save_dictionary(request):
    return upload_data(request, "grabarConfiguracion")


@csrf_exempt
def clean_database(request):
    if request.method == 'POST':
        url = "http://127.0.0.1:5000/limpiarDatos"
        response = post(url)
        if response.status_code == 200:
            # Procesa la respuesta del servidor remoto según sea necesario
            # response.text contiene la respuesta del servidor
            return HttpResponse('Base de datos limpia.')


@csrf_exempt
def make_request(request, request_id):
    if request.method == 'GET':
        # Obtén las fechas de la solicitud
        date_1 = request.GET.get('date_1')
        date_2 = request.GET.get('date_2')

        # Realiza la lógica deseada con las fechas y el request_id

        # Devuelve una respuesta HTTP apropiada
        return HttpResponse(f'Request {request_id} con Fecha 1: {date_1}, Fecha 2: {date_2}')


def return_hashtags(request):
    url = "http://127.0.0.1:5000/devolerHashtags"


def return_users(request):
    url = "http://127.0.0.1:5000/devolerMenciones"


def return_feelings(request):
    url = "http://127.0.0.1:5000/devolverSentimientos"


def get_info(request):
    return HttpResponse('Front IPC2')