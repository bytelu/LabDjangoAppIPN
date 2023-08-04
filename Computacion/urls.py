from django.urls import path
from .views import *

urlpatterns = [
    path('', acceso, name='acceso'),
    path('crearsesion_indiv/', crearsesion_indiv, name='crearsesion_indiv'),
    path('crearsesion_grupal/', crearsesion_grupal, name='crearsesion_grupal'),
]

