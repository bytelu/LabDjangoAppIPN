import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.db import transaction
from .models import Encargado, Computadora, Profesor, Estudiante, Carrera, Reporte, Sesion
from datetime import datetime
from django.db.models import Q
from django.contrib.auth import logout


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
def validacionA_encargado(request):
    nombre = request.POST.get("nombre")
    apellido_p = request.POST.get("apellido_p")
    apellido_m = request.POST.get("apellido_m")
    hora_entrada = request.POST.get("hora_entrada")
    hora_salida = request.POST.get("hora_salida")
    usuario = request.POST.get("usuario")
    contrasenia = request.POST.get("contrasenia")
    repcontrasenia = request.POST.get("repcontrasenia")
    
    # Verificar y formatear hora de entrada
    if not hora_entrada or not re.match(r'^\d{2}:\d{2}$', hora_entrada):
        hora_entrada = '00:00'
    # Verificar y formatear hora de salida
    if not hora_salida or not re.match(r'^\d{2}:\d{2}$', hora_salida):
        hora_salida = '00:00'

    # Reemplaza 'midnight' con '00:00' si es necesario
    if hora_entrada == 'midnight':
        hora_entrada = '00:00'
    if hora_salida == 'midnight':
        hora_salida = '00:00'

     # Verificar si el usuario ya existe en la base de datos por nombre completo
    if Encargado.objects.filter(Q(nombre=nombre) & Q(apellido_p=apellido_p) & Q(apellido_m=apellido_m)).exists():
        messages.error(request, "El encargado ya esta registrado.")
        return render(request, 'v_encargados/encargado.html', {
            'nombre': nombre,
            'apellido_p': apellido_p,
            'apellido_m': apellido_m,
            'hora_entrada': hora_entrada,
            'hora_salida': hora_salida,
            'usuario': usuario,
            'contrasenia': contrasenia,
            'repcontrasenia': repcontrasenia,
        })

    # Si no existe por nombre completo, verifica por el nombre de usuario
    if Encargado.objects.filter(usuario=usuario).exists():
        messages.error(request, "El nombre de usuario ya existe.")
        return render(request, 'v_encargados/encargados.html', {
            'nombre': nombre,
            'apellido_p': apellido_p,
            'apellido_m': apellido_m,
            'hora_entrada': hora_entrada,
            'hora_salida': hora_salida,
            'usuario': usuario,
            'contrasenia': contrasenia,
            'repcontrasenia': repcontrasenia,
        })

    if contrasenia == repcontrasenia:
        # Crear el encargado con la contraseña segura
        with transaction.atomic():
            encargado = Encargado(
                usuario=usuario,
                contrasenia=contrasenia,
                nombre=nombre,
                apellido_m=apellido_m,
                apellido_p=apellido_p,
                estado=1,
                hora_entrada=hora_entrada,
                hora_salida=hora_salida,
            )
            encargado.save()

        # Redireccionar al usuario a la página de inicio de sesión con mensaje de éxito
        messages.success(request, "Usuario registrado correctamente.")
        return redirect('encargados')  # Cambia 'pagina_de_inicio' al nombre de la URL adecuada
    else:
        messages.error(request, "Las contraseñas no coinciden.")
        return render(request, 'v_encargados/agregar_encargado.html', {
            'nombre': nombre,
            'apellido_p': apellido_p,
            'apellido_m': apellido_m,
            'hora_entrada': hora_entrada,
            'hora_salida': hora_salida,
            'usuario': usuario,
        })
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
    
    # Verificar y formatear hora de entrada
    if not hora_entrada or not re.match(r'^\d{2}:\d{2}$', hora_entrada):
        hora_entrada = '00:00'
    # Verificar y formatear hora de salida
    if not hora_salida or not re.match(r'^\d{2}:\d{2}$', hora_salida):
        hora_salida = '00:00'

    # Reemplaza 'midnight' con '00:00' si es necesario
    if hora_entrada == 'midnight':
        hora_entrada = '00:00'
    if hora_salida == 'midnight':
        hora_salida = '00:00'
    
    if contrasenia == repcontrasenia:
        Encargado.objects.filter(pk=id).update(nombre=nombre, apellido_m=apellido_m, apellido_p=apellido_p, hora_entrada=hora_entrada, hora_salida=hora_salida,usuario=usuario,contrasenia=contrasenia)
        messages.success(request, 'Encargado actualizado')
        return redirect('encargados')
    else:
        messages.error(request, "Las contraseñas no coinciden.")
        return render(request, 'v_encargados/editar_encargado.html', {
            'nombre': nombre,
            'apellido_p': apellido_p,
            'apellido_m': apellido_m,
            'hora_entrada': hora_entrada,
            'hora_salida': hora_salida,
            'usuario': usuario,
        })
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
    nombre = request.POST.get("nombre")
    apellido_p = request.POST.get("apellido_p")
    apellido_m = request.POST.get("apellido_m")
    boleta = request.POST.get("boleta")

    # Verificar si el profesor ya existe en la base de datos
    if Profesor.objects.filter(Q(nombre=nombre) & Q(apellido_p=apellido_p) & Q(apellido_m=apellido_m)).exists():
        messages.error(request, "El profesor ya existe.")
        return render(request, 'v_profesores/profesor.html', {
            'nombre': nombre,
            'apellido_p': apellido_p,
            'apellido_m': apellido_m,
            'boleta': boleta,
        })
    
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
    nombre = request.POST.get("nombre")
    apellido_p = request.POST.get("apellido_p")
    apellido_m = request.POST.get("apellido_m")
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
    nombre = request.POST.get("nombre")
    apellido_p = request.POST.get("apellido_p")
    apellido_m = request.POST.get("apellido_m")
    boleta = request.POST.get("boleta")
    id_carrera_id = request.POST.get("carrera")
    carrera = get_object_or_404(Carrera, id=id_carrera_id)
    
    # Verificar si el alumno ya existe en la base de datos
    if Estudiante.objects.filter(Q(nombre=nombre) & Q(apellido_p=apellido_p) & Q(apellido_m=apellido_m)).exists():
        messages.error(request, "El alumno ya esta registrado.")
        return render(request, 'v_alumnos/alumno.html', {
            'nombre': nombre,
            'apellido_p': apellido_p,
            'apellido_m': apellido_m,
            'boleta': boleta,
        })
        
    # Verificar si el alumno ya existe en la base de datos
    if Estudiante.objects.filter(Q(boleta=boleta)).exists():
        messages.error(request, "El numero de boleta ya esta asignado.")
        return render(request, 'v_alumnos/alumno.html', {
            'nombre': nombre,
            'apellido_p': apellido_p,
            'apellido_m': apellido_m,
            'boleta': boleta,
        })
    
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
    nombre = request.POST.get("nombre")
    apellido_p = request.POST.get("apellido_p")
    apellido_m = request.POST.get("apellido_m")
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
    estado = request.POST.get("estado")
    laboratorio = request.POST.get("laboratorio")
    cod_monitor = request.POST.get("cod_monitor")
    cod_cpu = request.POST.get("cod_cpu")
    ocupada = request.POST.get("ocupada")

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
    estado = request.POST.get("estado")
    laboratorio = request.POST.get("laboratorio")
    cod_monitor = request.POST.get("cod_monitor")
    cod_cpu = request.POST.get("cod_cpu")
    ocupada = request.POST.get("ocupada")
    
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
    activo = request.POST.get("activo")
    id_encargado_id = request.POST.get("encargado")
    encargado = get_object_or_404(Encargado, id=id_encargado_id)
    id_estudiante_id = request.POST.get("estudiante")
    estudiante = get_object_or_404(Estudiante, id=id_estudiante_id)
    id_computadora_id = request.POST.get("computadora")
    id_profesor_id = request.POST.get("profesor")

    # Verifica si se proporcionó una computadora
    if id_computadora_id:
        computadora = get_object_or_404(Computadora, id=id_computadora_id)
    else:
        computadora = None  # Establece el campo en None si no se proporcionó

    # Verifica si se proporcionó una computadora
    if id_profesor_id:
        profesor = get_object_or_404(Computadora, id=id_profesor_id)
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
    activo = request.POST.get("activo")
    id_encargado_id = request.POST.get("encargado")
    encargado = get_object_or_404(Encargado, id=id_encargado_id)
    id_estudiante_id = request.POST.get("estudiante")
    estudiante = get_object_or_404(Estudiante, id=id_estudiante_id)
    id_computadora_id = request.POST.get("computadora")
    id_profesor_id = request.POST.get("profesor")

    # Verifica si se proporcionó una computadora
    if id_computadora_id:
        computadora = get_object_or_404(Computadora, id=id_computadora_id)
    else:
        computadora = None  # Establece el campo en None si no se proporcionó

    # Verifica si se proporcionó una computadora
    if id_profesor_id:
        profesor = get_object_or_404(Computadora, id=id_profesor_id)
    else:
        profesor = None  # Establece el campo en None si no se proporcionó


    Sesion.objects.filter(pk=id).update(fecha=fecha, hora_inicio=hora_inicio, hora_final=hora_final, activo=activo, encargado_id=encargado, estudiante_id=estudiante,computadora_id=computadora, profesor_id=profesor)
    messages.success(request, 'Sesión actualizada')
    return redirect('sesiones_grupo')
def eliminar_grupos(request, id):
    sesion = Sesion.objects.filter(pk=id)
    sesion.delete()
    messages.success(request, 'Sesión eliminada')
    return redirect('sesiones_grupo')
# ----------------------------- VISTA DE SESIONES INDIVIDUALES ----------------------------------------- #
def sesiones_individual(request):
    pass
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