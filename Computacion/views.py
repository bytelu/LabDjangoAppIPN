import os, io, datetime, locale
import re
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.db import transaction
from .models import Encargado, Computadora, Profesor, Estudiante, Carrera, Reporte, Sesion
from django.db.models import Q
from django.contrib.auth import logout
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.http import HttpResponse
from reportlab.platypus import Image
from io import BytesIO
import requests
from django.shortcuts import get_object_or_404

# Create your views here.
def login (request):
    return render(request, 'login/login.html', {'es_registro': False})
def conn(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')

        # Consultar si existe un encargado con el usuario proporcionado
        try:
            encargado = Encargado.objects.get(usuario=usuario)
        except Encargado.DoesNotExist:
            # Si no se encuentra el usuario en la base de datos, mostrar un mensaje de error
            messages.error(request, 'El usuario no existe.')
            return redirect('login')

        # Comparar la contraseña ingresada 
        if (contrasenia, encargado.contrasenia):
            request.session['encargado_id'] = encargado.id
            return redirect('acceso')  # Aquí 'acceso' es el nombre de la URL a la que deseas redirigir
        else:
            # Las credenciales son inválidas, mostrar un mensaje de error
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('login')

    # Si no es una solicitud POST, renderizar el formulario de inicio de sesión
    return redirect('login')
def acceso(request):
    # Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()

    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
        # Consultar la base de datos para obtener la información del encargado
        encargado = Encargado.objects.get(id=encargado_id)

    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
    }

    return render(request, 'adminlte/index.html', context)
def registro(request):
    if request.method == 'POST':
        username = request.POST.get('usuario', '')
        password = request.POST.get('contrasenia', '')
        confirm_password = request.POST.get('contraseniados', '')
        nombre = request.POST.get('nombre', '')
        apellido_p = request.POST.get('a_paterno', '')
        apellido_m = request.POST.get('a_materno', '')

        # Verificar si el usuario ya existe en la base de datos
        if Encargado.objects.filter(usuario=username).exists():
            messages.error(request, "El usuario ya existe.")
            return render(request, 'login/login.html', {'es_registro': True})

        if password == confirm_password:
            # Crear el encargado con la contraseña segura
            with transaction.atomic():  # Usar una transacción para asegurar la consistencia de la base de datos
                encargado = Encargado(
                    usuario=username,
                    contrasenia=password,
                    nombre=nombre,
                    apellido_m=apellido_m,
                    apellido_p=apellido_p,
                    estado=1
                )
                encargado.save()

            # Redireccionar al usuario a la página de inicio de sesión con mensaje de éxito
            messages.success(request, "Usuario registrado correctamente.")
            return render(request, 'login/login.html', {'es_registro': True})

        else:
            # Si las contraseñas no coinciden, mostrar un mensaje de error en el formulario
            messages.error(request, "Las contraseñas no coinciden.")
            # Redireccionar al usuario al formulario de registro, pero manténer los datos de usuario ingresados
            # y borrar solo las contraseñas para que pueda volver a ingresarlas.
            return render(request, 'login/login.html', {'es_registro': True})

    # Si el método de solicitud es GET o hay algún otro error, muestra el formulario de registro
    # sin datos ingresados, para que el usuario pueda comenzar a registrarse.
    return render(request, 'login/login.html', {'es_registro': True})
# ----------------------------- VISTA DE ENCARGADOS ----------------------------------------- #
def encargados(request):
    # Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()

    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
        # Consultar la base de datos para obtener la información del encargado
        encargado = Encargado.objects.get(id=encargado_id)

    # Consultar la lista de todos los encargados
    encargados = Encargado.objects.all()

    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
        'encargados': encargados,  # Incluye la lista de todos los encargados
    }

    return render(request, 'v_encargados/encargado.html', context)
def validar_horas(hora):
    from datetime import datetime
    try:
        hora_datetime = datetime.strptime(hora, "%H:%M")
        return hora_datetime.time() >= datetime.strptime("07:00", "%H:%M").time() and \
               hora_datetime.time() <= datetime.strptime("22:00", "%H:%M").time()
    except ValueError:
        return False
def validacionA_encargado(request):
    nombre = request.POST.get("nombre").capitalize()
    apellido_p = request.POST.get("apellido_p").capitalize()
    apellido_m = request.POST.get("apellido_m").capitalize()
    hora_entrada = request.POST.get("hora_entrada")
    hora_salida = request.POST.get("hora_salida")
    usuario = request.POST.get("usuario")
    contrasenia = request.POST.get("contrasenia")
    repcontrasenia = request.POST.get("repcontrasenia")
    estado = int(request.POST.get("estado"))

    if validar_horas(hora_entrada) and validar_horas(hora_salida):
         # Verificar si el usuario ya existe en la base de datos por nombre completo
        if Encargado.objects.filter(Q(nombre=nombre) & Q(apellido_p=apellido_p) & Q(apellido_m=apellido_m)).exists():
            messages.error(request, "El encargado ya esta registrado.")
            return redirect('encargados')
        # Si no existe por nombre completo, verifica por el nombre de usuario
        if Encargado.objects.filter(usuario=usuario).exists():
            messages.error(request, "El nombre de usuario ya existe.")
            return redirect('encargados')

        if contrasenia == repcontrasenia:
            # Crear el encargado con la contraseña segura
            with transaction.atomic():
                encargado = Encargado(
                    usuario=usuario,
                    contrasenia=contrasenia,
                    nombre=nombre,
                    apellido_m=apellido_m,
                    apellido_p=apellido_p,
                    estado=estado,
                    hora_entrada=hora_entrada,
                    hora_salida=hora_salida,
                )
                encargado.save()

            # Redireccionar al usuario a la página de inicio de sesión con mensaje de éxito
            messages.success(request, "Usuario registrado correctamente.")
            return redirect('encargados')  # Cambia 'pagina_de_inicio' al nombre de la URL adecuada
        else:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('encargados')
    else:
        messages.error(request, "La asignacion de horas es de 7 am a 10 pm.")
        return redirect('encargados')      
def validacionE_encargado(request):
    id = request.POST.get("id")
    nombre = request.POST.get("nombre")
    apellido_p = request.POST.get("apellido_p")
    apellido_m = request.POST.get("apellido_m")
    hora_entrada = request.POST.get("hora_entrada")
    hora_salida = request.POST.get("hora_salida")
    usuario = request.POST.get("usuario")
    contrasenia = request.POST.get("contrasenia")
    repcontrasenia = request.POST.get("repcontrasenia")
    estado = int(request.POST.get("estado"))
    
    if validar_horas(hora_entrada) and validar_horas(hora_salida):
        if contrasenia == repcontrasenia:
            Encargado.objects.filter(pk=id).update(nombre=nombre, apellido_m=apellido_m, apellido_p=apellido_p, hora_entrada=hora_entrada, hora_salida=hora_salida,usuario=usuario,contrasenia=contrasenia, estado=estado)
            messages.success(request, 'Encargado actualizado')
            return redirect('encargados')
        else:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('encargados')
    else:
        messages.error(request, "La asignacion de horas es de 7 am a 10 pm.")
        return redirect('encargados')
def eliminar_encargado(request, id):
    encargado = Encargado.objects.filter(pk=id)
    encargado.delete()
    messages.success(request, 'Encargado eliminado')
    return redirect('encargados')
# ----------------------------- VISTA DE PROFESORES ----------------------------------------- #
def profesores(request):
     #Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()

    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
     # Consultar la base de datos para obtener la información del encargado
        encargado = Encargado.objects.get(id=encargado_id)

     #Consultar la lista de todos los encargados
    profesores = Profesor.objects.all()

     # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
        'profesores': profesores,  # Incluye la lista de todos los profesores
    }

    return render(request, 'v_profesores/profesor.html', context)
def validacionA_profesor(request):
    nombre = request.POST.get("nombre").capitalize()
    apellido_p = request.POST.get("apellido_p").capitalize()
    apellido_m = request.POST.get("apellido_m").capitalize()
    boleta = request.POST.get("boleta")

    # Verificar si el profesor ya existe en la base de datos
    if Profesor.objects.filter(Q(nombre=nombre) & Q(apellido_p=apellido_p) & Q(apellido_m=apellido_m)).exists():
        messages.error(request, "El profesor ya existe.")
        return redirect('profesores')
    else:
        # Crear el computadora si no existe
        profesor = Profesor(
            nombre=nombre,
            apellido_p=apellido_p,
            apellido_m=apellido_m,
            boleta=boleta,
        )
        profesor.save()
        # Redireccionar al usuario a la página de inicio de sesión con mensaje de éxito
        messages.success(request, "Profesor registrado correctamente.")
        return redirect('profesores')  # Cambia 'pagina_de_inicio' al nombre de la URL adecuada 
def validacionE_profesor(request):
    id = request.POST.get("id")
    nombre = request.POST.get("nombre").capitalize()
    apellido_p = request.POST.get("apellido_p").capitalize()
    apellido_m = request.POST.get("apellido_m").capitalize()
    boleta = request.POST.get("boleta")
    
    Profesor.objects.filter(pk=id).update(nombre=nombre, apellido_p=apellido_p, apellido_m=apellido_m, boleta=boleta)
    messages.success(request, 'Profesor actualizado')
    return redirect('profesores') 
def eliminar_profesor(request, id):
    profesor = Profesor.objects.filter(pk=id)
    profesor.delete()
    messages.success(request, 'Profesor eliminado')
    return redirect('profesores')
# ----------------------------- VISTA DE ALUMNOS ----------------------------------------- #
def alumnos(request):
   #  Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()
    carrera = Carrera.objects.all()

    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
     # Consultar la base de datos para obtener la información del encargado
       encargado = Encargado.objects.get(id=encargado_id)

     #Consultar la lista de todos los encargados
    alumnos = Estudiante.objects.all()

    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
        'alumnos': alumnos,  # Incluye la lista de todos los encargados
        'carrera' : carrera, 
    }

    return render(request, 'v_alumnos/alumno.html', context)
def validacionA_alumno(request):
    nombre = request.POST.get("nombre").capitalize()
    apellido_p = request.POST.get("apellido_p").capitalize()
    apellido_m = request.POST.get("apellido_m").capitalize()
    boleta = request.POST.get("boleta")
    id_carrera_id = request.POST.get("carrera")
    carrera = get_object_or_404(Carrera, id=id_carrera_id)
    
    # Verificar si el alumno ya existe en la base de datos
    if Estudiante.objects.filter(Q(nombre=nombre) & Q(apellido_p=apellido_p) & Q(apellido_m=apellido_m)).exists():
        messages.error(request, "El alumno ya esta registrado.")
        return redirect('alumnos') 
        
    # Verificar si el alumno ya existe en la base de datos
    if Estudiante.objects.filter(Q(boleta=boleta)).exists():
        messages.error(request, "El numero de boleta ya esta asignado.")
        return redirect('alumnos') 
    
    else:
        # Crear el alumno si no existe
        alumno = Estudiante(
            nombre=nombre,
            apellido_p=apellido_p,
            apellido_m=apellido_m,
            boleta=boleta,
            carrera=carrera,
        )
        alumno.save()
        # Redireccionar al usuario a la página de inicio de sesión con mensaje de éxito
        messages.success(request, "Alumno registrado correctamente.")
        return redirect('alumnos')  # Cambia 'pagina_de_inicio' al nombre de la URL adecuada    
def validacionE_alumno(request):
    id = request.POST.get("id")
    nombre = request.POST.get("nombre").capitalize()
    apellido_p = request.POST.get("apellido_p").capitalize()
    apellido_m = request.POST.get("apellido_m").capitalize()
    boleta = request.POST.get("boleta")
    id_carrera_id = request.POST.get("carrera")
    carrera = get_object_or_404(Carrera, id=id_carrera_id)
    
    Estudiante.objects.filter(pk=id).update(nombre=nombre, apellido_m=apellido_m, apellido_p=apellido_p, boleta=boleta, carrera_id = carrera)
    messages.success(request, 'Alumno actualizado')
    return redirect('alumnos') 
def eliminar_alumno(request,id):
    alumno = Estudiante.objects.filter(pk=id)
    alumno.delete()
    messages.success(request, 'Alumno eliminado')
    return redirect('alumnos')
# ----------------------------- VISTA DE COMPUTADORAS ----------------------------------------- #
def computadoras(request):
      # Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()

    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
        # Consultar la base de datos para obtener la información del encargado
        encargado = Encargado.objects.get(id=encargado_id)

    # Consultar la lista de todos los encargados
    computadoras = Computadora.objects.all()

    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
        'computadoras': computadoras,  # Incluye la lista de todas las computadoras
    }

    return render(request, 'v_computadoras/computadora.html', context)
def validacionA_computadora(request):
    numero = request.POST.get("numero")
    estado = int(request.POST.get("estado"))
    laboratorio = int(request.POST.get("laboratorio"))
    cod_monitor = request.POST.get("cod_monitor")
    cod_cpu = request.POST.get("cod_cpu")
    ocupada = int(request.POST.get("ocupada"))

    # Verificar si el la computadora ya existe en la base de datos
    if Computadora.objects.filter(Q(numero=numero) & Q(laboratorio=laboratorio)).exists():
        messages.error(request, "La computadora ya existe.")
        return render(request, 'v_computadoras/computadora.html', {
            'numero': numero,
            'estado': estado,
            'laboratorio': laboratorio,
            'cod_monitor': cod_monitor,
            'cod_cpu': cod_cpu,
            'ocupada': ocupada,
        })
    
    else:
        # Crear el computadora si no existe
        computadora = Computadora(
            numero=numero,
            estado=estado,
            laboratorio=laboratorio,
            cod_monitor=cod_monitor,
            cod_cpu=cod_cpu,
            ocupada=ocupada,
        )
        computadora.save()
        # Redireccionar al usuario a la página de inicio de sesión con mensaje de éxito
        messages.success(request, "Computadora registrada correctamente.")
        return redirect('computadoras')  # Cambia 'pagina_de_inicio' al nombre de la URL adecuada 
def validacionE_computadora(request):
    id = request.POST.get("id")
    numero = request.POST.get("numero")
    estado = int(request.POST.get("estado"))
    laboratorio = int(request.POST.get("laboratorio"))
    cod_monitor = request.POST.get("cod_monitor")
    cod_cpu = request.POST.get("cod_cpu")
    ocupada = int(request.POST.get("ocupada"))
    
    Computadora.objects.filter(pk=id).update(numero=numero, estado=estado, laboratorio=laboratorio, cod_monitor=cod_monitor, cod_cpu=cod_cpu, ocupada=ocupada)
    messages.success(request, 'Computadora actualizada')
    return redirect('computadoras') 
def eliminar_computadora(request, id):
    computadora = Computadora.objects.filter(pk=id)
    computadora.delete()
    messages.success(request, 'Computadora eliminada')
    return redirect('computadoras')
# ----------------------------- VISTA DE SESIONES DE GRUPO ----------------------------------------- #
def sesiones_grupo(request):
     #  Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()
    sesiones = Sesion.objects.all()

    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
     # Consultar la base de datos para obtener la información del encargado
       encargado = Encargado.objects.get(id=encargado_id)

    encargados = Encargado.objects.all()
    computadoras = Computadora.objects.all()
    estudiantes = Estudiante.objects.all()
    profesores = Profesor.objects.all()
    
    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
        'sesiones': sesiones,
        'encargado':encargados,
        'computadora':computadoras,
        'estudiante':estudiantes,
        'profesor':profesores,
    }

    return render(request, 'v_sesionesgrupo/grupo.html', context)
def validacionA_grupos(request):
    fecha = request.POST.get("fecha")
    hora_inicio = request.POST.get("hora_inicio")
    hora_final = request.POST.get("hora_final")
    activo = int(request.POST.get("activo"))
    id_encargado_id = request.POST.get("encargado")
    encargado = get_object_or_404(Encargado, id=id_encargado_id)
    id_estudiante_id = request.POST.get("estudiante")
    estudiante = get_object_or_404(Estudiante, id=id_estudiante_id)
    id_computadora_id = request.POST.get("computadora")
    id_profesor_id = request.POST.get("profesor")

    # Verifica si se proporcionó una computadora
    if id_computadora_id:
        computadora = get_object_or_404(Computadora, id=id_computadora_id)
        computadora.ocupada = 1
        computadora.save()
        
    else:
        computadora = None  # Establece el campo en None si no se proporcionó

    # Verifica si se proporcionó una computadora
    if id_profesor_id:
        profesor = get_object_or_404(Profesor, id=id_profesor_id)
    else:
        profesor = None  # Establece el campo en None si no se proporcionó

    sesion = Sesion(
        fecha=fecha,
        hora_final=hora_final,
        hora_inicio=hora_inicio,
        activo=activo,
        encargado=encargado,
        estudiante=estudiante,
        computadora=computadora,
        profesor=profesor,
    )
    sesion.save()
    # Redireccionar al usuario a la página de inicio de sesión con mensaje de éxito
    messages.success(request, "Sesion registrada correctamente.")
    return redirect('sesiones_grupo')  # Cambia 'pagina_de_inicio' al nombre de la URL adecuada
def validacionE_grupos(request):
    id = request.POST.get("id")
    fecha = request.POST.get("fecha")
    hora_inicio = request.POST.get("hora_inicio")
    hora_final = request.POST.get("hora_final")
    activo = int(request.POST.get("activo"))
    id_encargado_id = request.POST.get("encargado")
    encargado = get_object_or_404(Encargado, id=id_encargado_id)
    id_estudiante_id = request.POST.get("estudiante")
    estudiante = get_object_or_404(Estudiante, id=id_estudiante_id)
    id_computadora_id = request.POST.get("computadora")
    id_profesor_id = request.POST.get("profesor")

    # Verifica si se proporcionó una computadora
    if id_computadora_id:
        computadora = get_object_or_404(Computadora, id=id_computadora_id)
        computadora.ocupada = 1
        computadora.save()
    else:
        computadora = None  # Establece el campo en None si no se proporcionó

    # Verifica si se proporcionó una computadora
    if id_profesor_id:
        profesor = get_object_or_404(Profesor, id=id_profesor_id)
    else:
        profesor = None  # Establece el campo en None si no se proporcionó


    Sesion.objects.filter(pk=id).update(activo=activo, encargado_id=encargado, estudiante_id=estudiante,computadora_id=computadora)
    messages.success(request, 'Sesión actualizada')
    return redirect('sesiones_grupo')
def eliminar_grupos(request, id):
    sesion = Sesion.objects.filter(pk=id)
    sesion.delete()
    messages.success(request, 'Sesión eliminada')
    return redirect('sesiones_grupo')
# ----------------------------- VISTA DE SESIONES INDIVIDUALES ----------------------------------------- #
def sesiones_individual(request):
     #  Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()
    sesiones = Sesion.objects.all()

    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
     # Consultar la base de datos para obtener la información del encargado
       encargado = Encargado.objects.get(id=encargado_id)

    encargados = Encargado.objects.all()
    computadoras = Computadora.objects.all()
    estudiantes = Estudiante.objects.all()
    
    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
        'sesiones': sesiones,
        'encargado':encargados,
        'computadora':computadoras,
        'estudiante':estudiantes,
    }

    return render(request, 'v_sesionesindividual/individual.html', context)
def validacionA_individual(request):
    fecha = request.POST.get("fecha")
    hora_inicio = request.POST.get("hora_inicio")
    hora_final = request.POST.get("hora_final")
    activo =int(request.POST.get("activo"))
    id_encargado_id = request.POST.get("encargado")
    encargado = get_object_or_404(Encargado, id=id_encargado_id)
    id_estudiante_id = request.POST.get("estudiante")
    estudiante = get_object_or_404(Estudiante, id=id_estudiante_id)
    id_computadora_id = request.POST.get("computadora")

    # Verifica si se proporcionó una computadora
    if id_computadora_id:
        computadora = get_object_or_404(Computadora, id=id_computadora_id)
         # Actualiza el estado de la computadora a ocupada = 1
        computadora.ocupada = 1
        computadora.save()
    else:
        computadora = None  # Establece el campo en None si no se proporcionó

    sesion = Sesion(
        fecha=fecha,
        hora_final=hora_final,
        hora_inicio=hora_inicio,
        activo=activo,
        encargado=encargado,
        estudiante=estudiante,
        computadora=computadora,
        profesor=None,
    )
    sesion.save()
    # Redireccionar al usuario a la página de inicio de sesión con mensaje de éxito
    messages.success(request, "Sesion registrada correctamente.")
    return redirect('sesiones_individual')  # Cambia 'pagina_de_inicio' al nombre de la URL adecuada
def validacionE_individual(request):
    id = request.POST.get("id")
    fecha = request.POST.get("fecha")
    hora_inicio = request.POST.get("hora_inicio")
    hora_final = request.POST.get("hora_final")
    activo = int(request.POST.get("activo"))
    id_encargado_id = request.POST.get("encargado")
    encargado = get_object_or_404(Encargado, id=id_encargado_id)
    id_estudiante_id = request.POST.get("estudiante")
    estudiante = get_object_or_404(Estudiante, id=id_estudiante_id)
    id_computadora_id = request.POST.get("computadora")

    # Verifica si se proporcionó una computadora
    if id_computadora_id:
        computadora = get_object_or_404(Computadora, id=id_computadora_id)
        computadora.ocupada = 1
        computadora.save()
    else:
        computadora = None  # Establece el campo en None si no se proporcionó

    Sesion.objects.filter(pk=id).update(activo=activo, encargado_id=encargado, estudiante_id=estudiante,computadora_id=computadora, profesor_id=None)
    messages.success(request, 'Sesión actualizada')
    return redirect('sesiones_individual')
def eliminar_individual(request, id):
    sesion = Sesion.objects.filter(pk=id)
    sesion.delete()
    messages.success(request, 'Sesión eliminada')
    return redirect('sesiones_individual')
# ----------------------------- VISTA DE LABORATORIO 1 ----------------------------------------- #
def laboratorio_uno(request):
    #  Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()
    computadora = Computadora.objects.all()
    sesiones = Sesion.objects.all()
    
    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
     # Consultar la base de datos para obtener la información del encargado
       encargado = Encargado.objects.get(id=encargado_id)

    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
        'computadoras' : computadora,
        'sesiones': sesiones
    }

    return render(request, 'v_labuno/labuno.html', context)
# ----------------------------- VISTA DE LABORATORIO 2 ----------------------------------------- #
def laboratorio_dos(request):
    #  Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()
    computadora = Computadora.objects.all()
    sesiones = Sesion.objects.all()
    
    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
     # Consultar la base de datos para obtener la información del encargado
       encargado = Encargado.objects.get(id=encargado_id)

    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
        'computadoras' : computadora,
        'sesiones': sesiones
    }

    return render(request, 'v_labdos/labdos.html', context)
# ----------------------------- VISTA DE REPORTES ----------------------------------------- #
def reportes(request):
    #  Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()
    encargadoo = Encargado.objects.all()
    computadora = Computadora.objects.all()

    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
     # Consultar la base de datos para obtener la información del encargado
       encargado = Encargado.objects.get(id=encargado_id)

     #Consultar la lista de todos los encargados
    reportes = Reporte.objects.all()

    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
        'encargado': encargadoo,
        'computadora' : computadora,
        'reportes':reportes,
    }

    return render(request, 'v_reportes/reporte.html', context)
def validacionA_reportes(request):
    titulo = request.POST.get("titulo")
    descripcion = request.POST.get("descripcion")
    fecha = request.POST.get("fecha")
    hora = request.POST.get("hora")
    seguimiento = request.POST.get("seguimiento")
    id_encargado_id = request.POST.get("encargado")
    encargado = get_object_or_404(Encargado, id=id_encargado_id)
    id_computadora_id = request.POST.get("computadora")

    # Verifica si se proporcionó una computadora
    if id_computadora_id:
        computadora = get_object_or_404(Computadora, id=id_computadora_id)
    else:
        computadora = None  # Establece el campo en None si no se proporcionó

    reporte = Reporte(
        titulo=titulo,
        descripcion=descripcion,
        fecha=fecha,
        hora=hora,
        seguimiento=seguimiento,
        encargado=encargado,
        computadora=computadora,
    )
    reporte.save()
    # Redireccionar al usuario a la página de inicio de sesión con mensaje de éxito
    messages.success(request, "Reporte registrado correctamente.")
    return redirect('reportes')  # Cambia 'pagina_de_inicio' al nombre de la URL adecuada
def validacionE_reportes(request):
    id = request.POST.get("id")
    titulo = request.POST.get("titulo")
    descripcion = request.POST.get("descripcion")
    seguimiento = request.POST.get("seguimiento")
    id_encargado_id = request.POST.get("encargado")
    encargado = get_object_or_404(Encargado, id=id_encargado_id)
    id_computadora_id = request.POST.get("computadora")

    # Verifica si se proporcionó una computadora
    if id_computadora_id:
        computadora = get_object_or_404(Computadora, id=id_computadora_id)
    else:
        computadora = None  # Establece el campo en None si no se proporcionó

    Reporte.objects.filter(pk=id).update(titulo=titulo, descripcion=descripcion, seguimiento=seguimiento, encargado_id=encargado, computadora_id=computadora)
    messages.success(request, 'Reporte actualizado')
    return redirect('reportes')
def eliminar_reporte(request, id):
    reporte = Reporte.objects.filter(pk=id)
    reporte.delete()
    messages.success(request, 'Reporte eliminado')
    return redirect('reportes')
# ----------------------------- VISTA DE AYUDA ----------------------------------------- #
def ayuda(request):
      # Obtener el número de registros de tablas
    num_computadoras = Computadora.objects.count()
    num_profesores = Profesor.objects.count()
    num_encargados = Encargado.objects.count()
    num_estudiantes = Estudiante.objects.count()

    encargado_id = request.session.get('encargado_id')
    encargado = None

    if encargado_id:
        # Consultar la base de datos para obtener la información del encargado
        encargado = Encargado.objects.get(id=encargado_id)

    # Crear un contexto con todos los datos
    context = {
        'computadoras_lista': num_computadoras,
        'profesores_lista': num_profesores,
        'encargados_lista': num_encargados,
        'estudiantes_lista': num_estudiantes,
        'encargado_principal': encargado,  # Incluye también el encargado autenticado en el contexto
    }

    return render(request, 'v_ayuda/ayuda.html', context)
# ----------------------------- VISTA DE CERRAR SESION ----------------------------------------- #
def cerrar_sesion(request):
     # Cerrar la sesión del usuario
    logout(request)
    return redirect('login')  # Redirigir al usuario a la página de inicio de sesión

##################################### REPORTE ############################################
def draw_encabezado(pdf, titulo, nombre_encargado):

    # Color de fondo más grueso
    #pdf.setFillColorRGB(0.74, 0, 0.56)  # Color fiusha (ajustar según tus preferencias)
    #pdf.rect(0, 742, 612, 50, fill=True)

    # Ruta de la imagen en tu proyecto Django
    imagen_url = 'http://localhost:8000/static/img/educacion.jpg'  # Ajusta la URL según tu estructura de carpetas

    # Reducir las dimensiones de la imagen
    nueva_anchura = 100  # Por ejemplo, la mitad del ancho original
    nueva_altura = 80  # Por ejemplo, la mitad de la altura original

    # Calcular la posición para colocar la imagen en el encabezado
    x_imagen = 20
    y_imagen = 717  

    # Descargar la imagen utilizando requests
    response = requests.get(imagen_url)
    image_data = BytesIO(response.content)

    # Cargar la imagen como un objeto Image de ReportLab y ajustar sus dimensiones
    imagen = Image(image_data, width=nueva_anchura, height=nueva_altura)

    # Agregar la imagen al PDF en la posición específica
    imagen.drawOn(pdf, x_imagen, y_imagen)

    # Agregar una línea de separación
    pdf.setLineWidth(1)  # Ancho de la línea
    pdf.setStrokeColorRGB(0.427, 0.102, 0.259)  # Color IPN
    pdf.line(15, 735, 595, 737)  # Coordenadas de inicio y fin de la línea


    # Agregar una línea de separación
    pdf.setLineWidth(1)  # Ancho de la línea
    pdf.setStrokeColorRGB(0.705, 0.556, 0.365)  # Color DORADO
    pdf.line(122, 770, 122, 750)  # Coordenadas de inicio y fin de la línea

     # Ruta de la imagen en tu proyecto Django
    imagen_url2 = 'http://localhost:8000/static/img/ipnservicio.png'  # Ajusta la URL según tu estructura de carpetas

    # Reducir las dimensiones de la imagen
    nueva_anchura2 = 100  # Por ejemplo, la mitad del ancho original
    nueva_altura2 = 30  # Por ejemplo, la mitad de la altura original

    # Calcular la posición para colocar la imagen en el encabezado
    x_imagen2 = 130
    y_imagen2 = 742

    # Descargar la imagen utilizando requests
    response2 = requests.get(imagen_url2)
    image_data2 = BytesIO(response2.content)

    # Cargar la imagen como un objeto Image de ReportLab y ajustar sus dimensiones
    imagen2 = Image(image_data2, width=nueva_anchura2, height=nueva_altura2)

    # Agregar la imagen al PDF en la posición específica
    imagen2.drawOn(pdf, x_imagen2, y_imagen2)
    
    # Texto "EDUCACION del IPN" en la sección superior DERECHA
    pdf.setFont("Times-Italic", 8)  # Cambiado a un tipo de letra cursiva
    pdf.setFillColorRGB(0, 0, 0)  # Texto en color negro
    pdf.drawString(490, 761, "Ingeniería en Computación")
    pdf.drawString(484, 751, "Laboratorio de Computación")


    # Título del reporte
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColorRGB(0.427, 0.102, 0.259)  # Color fiusha
    pdf.drawString(200, 720, titulo)

    # Nombre del encargado
    pdf.setFont("Helvetica", 10)
    pdf.setFillColorRGB(0, 0, 0)  # Texto en negro
    pdf.drawString(50, 700, f"Encargado: {nombre_encargado}")

    # Dentro de la función que genera el PDF
    fecha_actual = datetime.datetime.now()

    # Configurar el locale para obtener la fecha en español
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    # Obtener la fecha y la hora por separado
    fecha_formateada = fecha_actual.strftime("%d de %B de %Y")
    hora_formateada = fecha_actual.strftime("%I:%M")

    # Agregar AM o PM manualmente
    am_pm = "AM" if fecha_actual.hour < 12 else "PM"
    pdf.setFont("Times-Italic", 10)  # Cambiado a un tipo de letra cursiva
    pdf.drawString(485, 725, f"{fecha_formateada}")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(430, 700, f"Hora de Impresión: {hora_formateada} {am_pm}")
def draw_pie_de_pagina(pdf, numero_pagina):
    # Diseño del pie de página aquí
    pdf.setFillColorRGB(0.427, 0.102, 0.259)  # Color de fondo
    pdf.rect(0, 0, 612, 50, fill=True)

    pdf.setFont("Helvetica", 8)
    pdf.setFillColorRGB(1, 1, 1)  # Color del texto
    pdf.drawString(30, 20, "Instituto Politécnico Nacional - Esime Culhuacan")

    # Agregar el número de página
    pdf.drawRightString(580, 20, f"Página {numero_pagina}")
def generar_computadoras(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 10)

    titulo = "Reporte de Computadoras"
    encargado_id = request.session.get('encargado_id') 
    encargado = Encargado.objects.get(id=encargado_id)
    nombre_encargado = f"{encargado.nombre} {encargado.apellido_p} {encargado.apellido_m}" if encargado else "Nombre del Encargado"

    pagina_actual = 1

    draw_encabezado(p, titulo, nombre_encargado)
    draw_pie_de_pagina(p, pagina_actual)

    data = Computadora.objects.all()

    table_header = ["Computadora", "Estado", "Laboratorio", "Código del Monitor", "Código del CPU", "Acción"]
    col_widths = [p.stringWidth(header, "Helvetica-Bold", 10) + 20 for header in table_header]
    col_widths[-1] += 30

    table_data = []

    for item in data:
        estado = "Activa" if item.estado == 1 else "Apagada"
        laboratorio = "Laboratorio 1" if item.laboratorio == 1 else "Laboratorio 2"
        ocupada = "Ocupada" if item.ocupada == 1 else "Desocupada"

        row = (str(item.numero), estado, laboratorio, item.cod_monitor, item.cod_cpu, ocupada)
        table_data.append(row)

    page_width, page_height = letter
    table_width = sum(col_widths)
    x = (page_width - table_width) / 2
    y = page_height - 130

    header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259)),  # Cambiar a tu primer color RGB
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ])

    table_header_data = [table_header]
    table_header = Table(table_header_data, colWidths=col_widths)
    table_header.setStyle(header_style)

    # Añadir la propiedad repeatRows para repetir el encabezado en todas las páginas
    header_style.add('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259))
    header_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)
    header_style.add('ALIGN', (0, 0), (-1, -1), 'CENTER')
    header_style.add('BOTTOMPADDING', (0, 0), (-1, 0), 12)
    header_style.add('LINEABOVE', (0, 0), (-1, 0), 1, colors.black)
    table_header.setStyle(header_style)

    table_header.wrapOn(p, 0, 0)
    table_header.drawOn(p, x, y)

    y -= 20

    for row in table_data:
        table_row_data = [row]
        table_row = Table(table_row_data, colWidths=col_widths)
        table_row_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        table_row.setStyle(table_row_style)

        if y <= 50:
            p.showPage()
            pagina_actual += 1
            draw_encabezado(p, titulo, nombre_encargado)
            draw_pie_de_pagina(p, pagina_actual)

            if pagina_actual != 1:
                y = page_height - 130

            # Dibujar el encabezado de la tabla en todas las páginas
            table_header.wrapOn(p, 0, 0)
            table_header.drawOn(p, x, y)
            y -= 20

        table_row.wrapOn(p, 0, 0)
        table_row.drawOn(p, x, y)
        y -= 20

    draw_pie_de_pagina(p, pagina_actual)
    p.save()

    pdf_content = buffer.getvalue()
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reporte_computadoras.pdf"'

    return response
def generar_laboratoriouno(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 10)

    titulo = "Sesión de Laboratorio 1"
    encargado_id = request.session.get('encargado_id') 
    encargado = Encargado.objects.get(id=encargado_id)
    nombre_encargado = f"{encargado.nombre} {encargado.apellido_p} {encargado.apellido_m}" if encargado else "Nombre del Encargado"

    pagina_actual = 1

    draw_encabezado(p, titulo, nombre_encargado)
    draw_pie_de_pagina(p, pagina_actual)

    sesion = Sesion.objects.filter(activo=1, computadora__laboratorio=1).order_by('id').first()

    if sesion:
        print("sesion encontrada")
        p.setFont("Helvetica", 10) # Cambiado a un tipo de letra cursiva
        p.setFillColorRGB(0, 0, 0)  # Texto en color negro
        #fecha_info = sesion.fecha.strftime("%d de %B de %Y")
        profesor_informacion = ""
        if sesion.profesor:
            profesor_informacion = f"{sesion.profesor.nombre} {sesion.profesor.apellido_p} {sesion.profesor.apellido_m}"
        hora_inicio_informacion = sesion.hora_inicio.strftime("%I:%M %p")
        hora_final_informacion = sesion.hora_final.strftime("%I:%M %p") if sesion.hora_final else "Sin finalizar"

        # Obtener AM o PM manualmente
        am_pm_inicio = "AM" if sesion.hora_inicio.hour < 12 else "PM"
        am_pm_final = "AM" if (sesion.hora_final.hour if sesion.hora_final else 0) < 12 else "PM"

        #laboratorio_info = sesion.computadora.laboratorio if sesion.computadora else "Sin computadora"

        x_position = 50
        y_position = 690

        #p.drawString(x_position, y_position, f"Fecha de Sesión: {fecha_info}")
        p.drawString(x_position, y_position-3, f"Profesor: {profesor_informacion}")
        p.drawString(x_position + 305, y_position-3, f"Hora Inicio: {hora_inicio_informacion} {am_pm_inicio} |")
        p.drawString(x_position + 413, y_position-3, f"Hora Final: {hora_final_informacion} {am_pm_final}")
        #p.drawString(x_position, y_position - 60, f"Laboratorio: {laboratorio_info}")
    else:
        p.drawString(100, 700, "No se encontró ninguna sesión que cumpla con los criterios.")

    data = Sesion.objects.filter(activo=1,computadora__laboratorio=1)
    table_header = ["Estudiante", "No. Computadora", "Carrera"]
    col_widths = [200,  # Ancho de la primera columna
              100,   # Ancho de la segunda columna
              150]  # Ancho de la tercera columna
    col_widths[-1] += 30  # Ajuste del último valor si es necesario

    table_data = []

    for sesion in data:
        estudiante_info = f"{sesion.estudiante.nombre} {sesion.estudiante.apellido_p} {sesion.estudiante.apellido_m}"
        carrera_info = f"{sesion.estudiante.carrera.carrera}"
        no_computadora_info = sesion.computadora.numero if sesion.computadora else "Sin computadora"
        row = [estudiante_info, no_computadora_info, carrera_info]
        table_data.append(row)

    page_width, page_height = letter
    table_width = sum(col_widths)
    x = (page_width - table_width) / 2
    y = page_height - 150

    header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259)),  # Cambiar a tu primer color RGB
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ])

    table_header_data = [table_header]
    table_header = Table(table_header_data, colWidths=col_widths)
    table_header.setStyle(header_style)

    # Añadir la propiedad repeatRows para repetir el encabezado en todas las páginas
    header_style.add('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259))
    header_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)
    header_style.add('ALIGN', (0, 0), (-1, -1), 'CENTER')
    header_style.add('BOTTOMPADDING', (0, 0), (-1, 0), 12)
    header_style.add('LINEABOVE', (0, 0), (-1, 0), 1, colors.black)
    table_header.setStyle(header_style)

    table_header.wrapOn(p, 0, 0)
    table_header.drawOn(p, x, y)

    y -= 20

    for row in table_data:
        table_row_data = [row]
        table_row = Table(table_row_data, colWidths=col_widths)
        table_row_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        table_row.setStyle(table_row_style)

        if y <= 50:
            p.showPage()
            pagina_actual += 1
            draw_encabezado(p, titulo, nombre_encargado)
            draw_pie_de_pagina(p, pagina_actual)

            if pagina_actual != 1:
                y = page_height - 150

            # Dibujar el encabezado de la tabla en todas las páginas
            table_header.wrapOn(p, 0, 0)
            table_header.drawOn(p, x, y)
            y -= 20

        table_row.wrapOn(p, 0, 0)
        table_row.drawOn(p, x, y)
        y -= 20

    draw_pie_de_pagina(p, pagina_actual)
    p.save()

    pdf_content = buffer.getvalue()
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reporte_SesionGrupal1.pdf"'

    return response
def generar_laboratoriodos(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 10)

    titulo = "Sesión de Laboratorio 2"
    encargado_id = request.session.get('encargado_id') 
    encargado = Encargado.objects.get(id=encargado_id)
    nombre_encargado = f"{encargado.nombre} {encargado.apellido_p} {encargado.apellido_m}" if encargado else "Nombre del Encargado"

    pagina_actual = 1

    draw_encabezado(p, titulo, nombre_encargado)
    draw_pie_de_pagina(p, pagina_actual)

    sesion = Sesion.objects.filter(activo=1, computadora__laboratorio=2).order_by('id').first()

    if sesion:
        print("sesion encontrada")
        p.setFont("Helvetica", 10) # Cambiado a un tipo de letra cursiva
        p.setFillColorRGB(0, 0, 0)  # Texto en color negro
        #fecha_info = sesion.fecha.strftime("%d de %B de %Y")
        profesor_informacion = f"{sesion.profesor.nombre} {sesion.profesor.apellido_p} {sesion.profesor.apellido_m}"
        hora_inicio_informacion = sesion.hora_inicio.strftime("%I:%M %p")
        hora_final_informacion = sesion.hora_final.strftime("%I:%M %p") if sesion.hora_final else "Sin finalizar"

        # Obtener AM o PM manualmente
        am_pm_inicio = "AM" if sesion.hora_inicio.hour < 12 else "PM"
        am_pm_final = "AM" if (sesion.hora_final.hour if sesion.hora_final else 0) < 12 else "PM"

        #laboratorio_info = sesion.computadora.laboratorio if sesion.computadora else "Sin computadora"

        x_position = 50
        y_position = 690

        #p.drawString(x_position, y_position, f"Fecha de Sesión: {fecha_info}")
        p.drawString(x_position, y_position-3, f"Profesor: {profesor_informacion}")
        p.drawString(x_position + 305, y_position-3, f"Hora Inicio: {hora_inicio_informacion} {am_pm_inicio} |")
        p.drawString(x_position + 413, y_position-3, f"Hora Final: {hora_final_informacion} {am_pm_final}")
        #p.drawString(x_position, y_position - 60, f"Laboratorio: {laboratorio_info}")
    else:
        p.drawString(100, 700, "No se encontró ninguna sesión que cumpla con los criterios.")

    data = Sesion.objects.filter(activo=1,computadora__laboratorio=2)
    table_header = ["Estudiante", "No. Computadora", "Carrera"]
    col_widths = [200,  # Ancho de la primera columna
              100,   # Ancho de la segunda columna
              150]  # Ancho de la tercera columna
    col_widths[-1] += 30  # Ajuste del último valor si es necesario

    table_data = []

    for sesion in data:
        estudiante_info = f"{sesion.estudiante.nombre} {sesion.estudiante.apellido_p} {sesion.estudiante.apellido_m}"
        carrera_info = f"{sesion.estudiante.carrera.carrera}"
        no_computadora_info = sesion.computadora.numero if sesion.computadora else "Sin computadora"
        row = [estudiante_info, no_computadora_info, carrera_info]
        table_data.append(row)

    page_width, page_height = letter
    table_width = sum(col_widths)
    x = (page_width - table_width) / 2
    y = page_height - 150

    header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259)),  # Cambiar a tu primer color RGB
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ])

    table_header_data = [table_header]
    table_header = Table(table_header_data, colWidths=col_widths)
    table_header.setStyle(header_style)

    # Añadir la propiedad repeatRows para repetir el encabezado en todas las páginas
    header_style.add('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259))
    header_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)
    header_style.add('ALIGN', (0, 0), (-1, -1), 'CENTER')
    header_style.add('BOTTOMPADDING', (0, 0), (-1, 0), 12)
    header_style.add('LINEABOVE', (0, 0), (-1, 0), 1, colors.black)
    table_header.setStyle(header_style)

    table_header.wrapOn(p, 0, 0)
    table_header.drawOn(p, x, y)

    y -= 20

    for row in table_data:
        table_row_data = [row]
        table_row = Table(table_row_data, colWidths=col_widths)
        table_row_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        table_row.setStyle(table_row_style)

        if y <= 50:
            p.showPage()
            pagina_actual += 1
            draw_encabezado(p, titulo, nombre_encargado)
            draw_pie_de_pagina(p, pagina_actual)

            if pagina_actual != 1:
                y = page_height - 150

            # Dibujar el encabezado de la tabla en todas las páginas
            table_header.wrapOn(p, 0, 0)
            table_header.drawOn(p, x, y)
            y -= 20

        table_row.wrapOn(p, 0, 0)
        table_row.drawOn(p, x, y)
        y -= 20

    draw_pie_de_pagina(p, pagina_actual)
    p.save()

    pdf_content = buffer.getvalue()
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reporte_SesionGrupal2.pdf"'

    return response
def generar_individual(request, sesion_id):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 10)

    # Buscar la sesión específica o devolver un error 404 si no se encuentra
    sesion = get_object_or_404(Sesion, id=sesion_id)
    print("sesion encontrada")
    titulo = f"Sesión Individual de Laboratorio {sesion.computadora.laboratorio}"
    encargado_id = request.session.get('encargado_id') 
    encargado = Encargado.objects.get(id=encargado_id)
    nombre_encargado = f"{encargado.nombre} {encargado.apellido_p} {encargado.apellido_m}" if encargado else "Nombre del Encargado"

    pagina_actual = 1

    draw_encabezado(p, titulo, nombre_encargado)
    draw_pie_de_pagina(p, pagina_actual)
    p.setFont("Helvetica", 10) # Cambiado a un tipo de letra cursiva
    p.setFillColorRGB(0, 0, 0)  # Texto en color negro

    hora_inicio_informacion = sesion.hora_inicio.strftime("%I:%M %p")
    hora_final_informacion = sesion.hora_final.strftime("%I:%M %p") if sesion.hora_final else "Sin finalizar"

    # Obtener AM o PM manualmente
    am_pm_inicio = "AM" if sesion.hora_inicio.hour < 12 else "PM"
    am_pm_final = "AM" if (sesion.hora_final.hour if sesion.hora_final else 0) < 12 else "PM"

    x_position = 50
    y_position = 690

    p.drawString(x_position + 305, y_position-3, f"Hora Inicio: {hora_inicio_informacion} {am_pm_inicio} |")
    p.drawString(x_position + 413, y_position-3, f"Hora Final: {hora_final_informacion} {am_pm_final}")

    data = [sesion]  # Utilizar solo la sesión específica

    table_header = ["Estudiante", "No. Computadora", "Carrera"]
    col_widths = [200, 100, 150]  # Ancho de las columnas
    col_widths[-1] += 30  # Ajuste del último valor si es necesario

    table_data = []

    for sesion in data:
        estudiante_info = f"{sesion.estudiante.nombre} {sesion.estudiante.apellido_p} {sesion.estudiante.apellido_m}"
        carrera_info = f"{sesion.estudiante.carrera.carrera}"
        no_computadora_info = sesion.computadora.numero if sesion.computadora else "Sin computadora"
        row = [estudiante_info, no_computadora_info, carrera_info]
        table_data.append(row)

    page_width, page_height = letter
    table_width = sum(col_widths)
    x = (page_width - table_width) / 2
    y = page_height - 150

    header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ])

    table_header_data = [table_header]
    table_header = Table(table_header_data, colWidths=col_widths)
    table_header.setStyle(header_style)

    header_style.add('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259))
    header_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)
    header_style.add('ALIGN', (0, 0), (-1, -1), 'CENTER')
    header_style.add('BOTTOMPADDING', (0, 0), (-1, 0), 12)
    header_style.add('LINEABOVE', (0, 0), (-1, 0), 1, colors.black)
    table_header.setStyle(header_style)

    table_header.wrapOn(p, 0, 0)
    table_header.drawOn(p, x, y)

    y -= 20

    for row in table_data:
        table_row_data = [row]
        table_row = Table(table_row_data, colWidths=col_widths)
        table_row_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        table_row.setStyle(table_row_style)

        if y <= 50:
            p.showPage()
            pagina_actual += 1
            draw_encabezado(p, titulo, nombre_encargado)
            draw_pie_de_pagina(p, pagina_actual)

            if pagina_actual != 1:
                y = page_height - 150

            table_header.wrapOn(p, 0, 0)
            table_header.drawOn(p, x, y)
            y -= 20

        table_row.wrapOn(p, 0, 0)
        table_row.drawOn(p, x, y)
        y -= 20

    draw_pie_de_pagina(p, pagina_actual)
    p.save()

    pdf_content = buffer.getvalue()
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reporte_Individual.pdf"'

    return response
def generar_reporte(request, reporte_id):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 10)

    # Buscar la sesión específica o devolver un error 404 si no se encuentra
    sesion = get_object_or_404(Reporte, id=reporte_id)
    print("sesion encontrada")
    titulo = f"Reporte: {sesion.titulo}"
    encargado_id = request.session.get('encargado_id') 
    encargado = Encargado.objects.get(id=encargado_id)
    nombre_encargado = f"{encargado.nombre} {encargado.apellido_p} {encargado.apellido_m}" if encargado else "Nombre del Encargado"

    pagina_actual = 1

    draw_encabezado(p, titulo, nombre_encargado)
    draw_pie_de_pagina(p, pagina_actual)
    p.setFont("Helvetica", 10) # Cambiado a un tipo de letra cursiva
    p.setFillColorRGB(0, 0, 0)  # Texto en color negro

    hora_inicio_informacion = sesion.hora.strftime("%I:%M %p")
    fecha_formateada = sesion.fecha.strftime("%d de %B de %Y")

    # Obtener AM o PM manualmente
    am_pm_inicio = "AM" if sesion.hora.hour < 12 else "PM"

    x_position = 50
    y_position = 690

    p.drawString(x_position, y_position-3, f"Generado el: {fecha_formateada} a las {hora_inicio_informacion}{am_pm_inicio} ")

    data = [sesion]  # Utilizar solo la sesión específica

    table_header = ["Encargado","Descripción", "Seguimiento", "Computadora"]
    col_widths = [130, 220, 100, 50]  # Ancho de las columnas
    col_widths[-1] += 30  # Ajuste del último valor si es necesario

    limite_caracteres = 30
    table_data = []

    for sesion in data:
        encargado_info = f"{sesion.encargado.nombre} {sesion.encargado.apellido_p} {sesion.encargado.apellido_m}"
        # Verificar si la descripción supera el límite de caracteres
        if len(sesion.descripcion) > limite_caracteres:
            # Dividir la descripción en partes más pequeñas
            partes_descripcion = [sesion.descripcion[i:i+limite_caracteres] for i in range(0, len(sesion.descripcion), limite_caracteres)]
            descripcion_info = "\n".join(partes_descripcion)
        else:
            descripcion_info = sesion.descripcion
        seguimiento_info = f"{sesion.seguimiento}"
        no_computadora_info = sesion.computadora.numero if sesion.computadora else "Ninguna"
        row = [encargado_info, descripcion_info, seguimiento_info,no_computadora_info]
        table_data.append(row)

    page_width, page_height = letter
    table_width = sum(col_widths)
    x = (page_width - table_width) / 2
    y = page_height - 150

    header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ])

    table_header_data = [table_header]
    table_header = Table(table_header_data, colWidths=col_widths)
    table_header.setStyle(header_style)

    header_style.add('BACKGROUND', (0, 0), (-1, 0), (0.427, 0.102, 0.259))
    header_style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)
    header_style.add('ALIGN', (0, 0), (-1, -1), 'CENTER')
    header_style.add('BOTTOMPADDING', (0, 0), (-1, 0), 12)
    header_style.add('LINEABOVE', (0, 0), (-1, 0), 1, colors.black)
    table_header.setStyle(header_style)

    table_header.wrapOn(p, 0, 0)
    table_header.drawOn(p, x, y)

    y -= 45

    for row in table_data:
        table_row_data = [row]
        table_row = Table(table_row_data, colWidths=col_widths)
        table_row_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        table_row.setStyle(table_row_style)

        if y <= 50:
            p.showPage()
            pagina_actual += 1
            draw_encabezado(p, titulo, nombre_encargado)
            draw_pie_de_pagina(p, pagina_actual)

            if pagina_actual != 1:
                y = page_height - 150

            table_header.wrapOn(p, 0, 0)
            table_header.drawOn(p, x, y)
            y -= 20

        table_row.wrapOn(p, 0, 0)
        table_row.drawOn(p, x, y)
        y -= 20

    draw_pie_de_pagina(p, pagina_actual)
    p.save()

    pdf_content = buffer.getvalue()
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reporte_Reportes.pdf"'

    return response
