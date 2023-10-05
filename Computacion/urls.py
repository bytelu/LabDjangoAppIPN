from django.urls import path
from .views import *
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', acceso, name='acceso'),
    #------------------------------VISTA DE ENCARGADOS (LISTO)--------------------#
    path('encargados/', encargados, name='encargados'),
    path('encargados/validandoA/', views.validacionA_encargado, name='validacionA_encargado'),
    path('encargados/validandoE', views.validacionE_encargado, name='validacionE_encargado'),
    path('encargados/eliminar/<int:id>/', views.eliminar_encargado, name='eliminar_encargado'),
    #------------------------------VISTA DE PROFESORES (LISTO)--------------------#
    path('profesores/', profesores, name='profesores'),
    path('profesores/validandoA/', views.validacionA_profesor, name='validacionA_profesor'),
    path('profesores/validandoE/', views.validacionE_profesor, name='validacionE_profesor'),
    path('profesores/eliminar/<int:id>/', views.eliminar_profesor, name='eliminar_profesor'),
    #------------------------------VISTA DE ALUMNOS (LISTO)--------------------#
    path('alumnos/', alumnos, name='alumnos'),
    path('alumnos/validandoA/', views.validacionA_alumno, name='validacionA_alumno'),
    path('alumnos/validandoE', views.validacionE_alumno, name='validacionE_alumno'),
    path('alumnos/eliminar/<int:id>/', views.eliminar_alumno, name='eliminar_alumno'),
    #------------------------------VISTA DE COMPUTADORAS (LISTO)--------------------#
    path('computadoras/', computadoras, name='computadoras'),
    path('computadoras/validandoA/', views.validacionA_computadora, name='validacionA_computadora'),
    path('computadoras/validandoE/', views.validacionE_computadora, name='validacionE_computadora'),
    path('computadoras/eliminar/<int:id>/', views.eliminar_computadora, name='eliminar_computadora'),
    #------------------------------VISTA DE SESIONES DE GRUPO--------------------#
    path('sesionesgrupo/', sesiones_grupo, name='sesiones_grupo'),
    path('grupos/validandoA/', views.validacionA_grupos, name='validacionA_grupos'),
    path('grupos/validandoE/', views.validacionE_grupos, name='validacionE_grupos'),
    path('grupos/eliminar/<int:id>/', views.eliminar_grupos, name='eliminar_grupo'),
    #------------------------------VISTA DE SESIONES INDIVIDUALES--------------------#
    path('sesionesindividual/', sesiones_individual, name='sesiones_individual'),
    path('individual/validandoA/', views.validacionA_individual, name='validacionA_individual'),
    path('individual/validandoE/', views.validacionE_individual, name='validacionE_individual'),
    path('individual/eliminar/<int:id>/', views.eliminar_individual, name='eliminar_individual'),
    #------------------------------VISTA DE LABORATORIO 1--------------------#
    path('laboratoriouno/', laboratorio_uno, name='laboratorio_uno'),
    #------------------------------VISTA DE LABORATORIO 2--------------------#
    path('laboratoriodos/', laboratorio_dos, name='laboratorio_dos'),
    #------------------------------VISTA DE REPORTES--------------------#
    path('reportes/', reportes, name='reportes'),
    path('reportes/validandoA/', views.validacionA_reportes, name='validacionA_reporte'),
    path('reportes/validandoE/', views.validacionE_reportes, name='validacionE_reporte'),
    path('reportes/eliminar/<int:id>/', views.eliminar_reporte, name='eliminar_reporte'),
    #------------------------------VISTA DE AYUDA--------------------#
    path('ayuda/', ayuda, name='ayuda'),
    #------------------------------VISTA DE CERRAR SESION--------------------#
    path('cerrar-sesion/', cerrar_sesion, name='cerrar_sesion'),
    #------------------------------VISTA DE REPORTES PDF--------------------#
    path('generar-computadoras/', views.generar_computadoras, name='generar_computadoras'),
    path('generar-laboratoriouno/', views.generar_laboratoriouno, name='generar_laboratoriouno'),
    path('generar-laboratoriodos/', views.generar_laboratoriodos, name='generar_laboratoriodos'),
    path('generar-individual/<int:sesion_id>/', views.generar_individual, name='generar_individual'),
    path('generar-reporte/<int:reporte_id>/', views.generar_reporte, name='generar_reporte'),

]

