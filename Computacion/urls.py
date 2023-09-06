from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', acceso, name='acceso'),
    #------------------------------VISTA DE ENCARGADOS--------------------#
    path('encargados/', encargados, name='encargados'),
    path('encargados/agregar/', views.agregar_encargado, name='agregar_encargado'),
    path('encargados/editar/<int:id>/', views.editar_encargado, name='editar_encargado'),
    path('encargados/eliminar/<int:id>/', views.eliminar_encargado, name='eliminar_encargado'),
]

