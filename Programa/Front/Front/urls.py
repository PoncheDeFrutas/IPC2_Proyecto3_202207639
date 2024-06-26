"""
URL configuration for Front project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Front.view import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', index),
    path('upload_messages_xml/', save_messages, name='upload_messages_xml'),
    path('upload_dictionary_xml/', save_dictionary, name='upload_dictionary_xml'),
    path('clean_database/', clean_database, name='clean_database'),
    path('make_request/<int:request_id>/', make_request, name='make_request')
]
