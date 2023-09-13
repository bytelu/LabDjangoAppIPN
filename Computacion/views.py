from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.db import transaction
from .models import Encargado, Computadora, Profesor, Estudiante, Carrera
from datetime import datetime


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

    # Verificar si el usuario ya existe en la base de datos
    if Encargado.objects.filter(usuario=usuario).exists():
        messages.error(request, "El usuario ya existe.")
        return render(request, 'v_encargados/agregar_encargado.html', {
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
def agregar_profesor(request):
    pass
def editar_profesor(request):
    pass
def eliminar_profesor(request):
    pass
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
    if Estudiante.objects.filter(nombre=nombre).exists():
        messages.error(request, "El alumno ya existe.")
        return render(request, 'v_alumnos/alumnos.html', {
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
    if Computadora.objects.filter(cod_monitor=cod_monitor).exists():
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
def eliminar_computadora(request):
    pass
# ----------------------------- VISTA DE SESIONES DE GRUPO ----------------------------------------- #
def sesiones_grupo(request):
    pass
# ----------------------------- VISTA DE SESIONES INDIVIDUALES ----------------------------------------- #
def sesiones_individual(request):
    pass
# ----------------------------- VISTA DE LABORATORIO 1 ----------------------------------------- #
def laboratorio_uno(request):
    pass
# ----------------------------- VISTA DE LABORATORIO 2 ----------------------------------------- #
def laboratorio_dos(request):
    pass
# ----------------------------- VISTA DE REPORTES ----------------------------------------- #
def reportes(request):
    pass
def agregar_reporte(request):
    pass
def editar_reporte(request):
    pass
def eliminar_reporte(request):
    pass
# ----------------------------- VISTA DE PERFIL ----------------------------------------- #
def perfil(request):
    pass
# ----------------------------- VISTA DE AYUDA ----------------------------------------- #
def ayuda(request):
    pass
# ----------------------------- VISTA DE CERRAR SESION ----------------------------------------- #
def cerrar_sesion(request):
    pass