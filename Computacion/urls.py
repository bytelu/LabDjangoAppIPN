from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', acceso, name='acceso'),
    #------------------------------VISTA DE ENCARGADOS--------------------#
    path('encargados/', encargados, name='encargados'),
    path('encargados/agregar/', views.agregar_encargado, name='agregar_encargado'),
    path('encargados/validandoA/', views.validacionA_encargado, name='validacionA_encargado'),
    path('encargados/editar/<int:id>/', views.editar_encargado, name='editar_encargado'),
    path('encargados/validandoE', views.validacionE_encargado, name='validacionE_encargado'),
    path('encargados/eliminar/<int:id>/', views.eliminar_encargado, name='eliminar_encargado'),
    #------------------------------VISTA DE PROFESORES--------------------#
    path('profesores/', profesores, name='profesores'),
    path('profesores/agregar/', views.agregar_profesor, name='agregar_profesor'),
    path('profesores/editar/<int:id>/', views.editar_profesor, name='editar_profesor'),
    path('profesores/eliminar/<int:id>/', views.eliminar_profesor, name='eliminar_profesor'),
    #------------------------------VISTA DE ALUMNOS--------------------#
    path('alumnos/', alumnos, name='alumnos'),
    path('alumnos/agregar/', views.agregar_alumno, name='agregar_alumno'),
    path('alumnos/validandoA/', views.validacionA_alumno, name='validacionA_alumno'),
    path('alumnos/editar/<int:id>/', views.editar_alumno, name='editar_alumno'),
    path('alumnos/validandoE', views.validacionE_alumno, name='validacionE_alumno'),
    path('alumnos/eliminar/<int:id>/', views.eliminar_alumno, name='eliminar_alumno'),
    #------------------------------VISTA DE COMPUTADORAS--------------------#
    path('computadoras/', computadoras, name='computadoras'),
    path('computadoras/agregar/', views.agregar_computadora, name='agregar_computadora'),
    path('computadoras/editar/<int:id>/', views.editar_computadora, name='editar_computadora'),
    path('computadoras/eliminar/<int:id>/', views.eliminar_computadora, name='eliminar_computadora'),
    #------------------------------VISTA DE SESIONES DE GRUPO--------------------#
    path('sesionesgrupo/', sesiones_grupo, name='sesiones_grupo'),
    #------------------------------VISTA DE SESIONES INDIVIDUALES--------------------#
    path('sesionesindividual/', sesiones_individual, name='sesiones_individual'),
    #------------------------------VISTA DE LABORATORIO 1--------------------#
    path('laboratoriouno/', laboratorio_uno, name='laboratorio_uno'),
    #------------------------------VISTA DE LABORATORIO 2--------------------#
    path('laboratoriodos/', laboratorio_dos, name='laboratorio_dos'),
    #------------------------------VISTA DE REPORTES--------------------#
    path('reportes/', reportes, name='reportes'),
    path('reportes/agregar/', views.agregar_reporte, name='agregar_reporte'),
    path('reportes/editar/<int:id>/', views.editar_reporte, name='editar_reporte'),
    path('reportes/eliminar/<int:id>/', views.eliminar_reporte, name='eliminar_reporte'),
    #------------------------------VISTA DE PERFIL--------------------#
    path('perfil/', perfil, name='perfil'),
    #------------------------------VISTA DE AYUDA--------------------#
    path('ayuda/', ayuda, name='ayuda'),
    #------------------------------VISTA DE CERRAR SESION--------------------#
    path('cerrarsesion/', cerrar_sesion, name='cerrar_sesion'),

]

