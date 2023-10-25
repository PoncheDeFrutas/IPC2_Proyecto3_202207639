"""
URL configuration for New_Front project.

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
from django.urls import path
from New_Front.views import *

urlpatterns = [
    path('', index, name='index'),
    path('reset/', reset_data, name='reset_data'),
    path('load_messages/', load_messages, name='load_messages'),
    path('load_dictionary/', load_dictionary, name='load_dictionary'),
    path('requests/', requests, name='requests'),
    path('upload_file', upload_file, name='upload_file'),
    path('results/', results, name='results'),
    path('graphics/', graphics, name='graphics'),
    path('show_pdf/', show_pdf, name='show_pdf')
]
