from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.db import transaction
from .models import Encargado, Computadora, Profesor, Estudiante


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
        'computadoras': num_computadoras,
        'profesores': num_profesores,
        'encargados': num_encargados,
        'estudiantes': num_estudiantes,
        'encargado': encargado,  # Incluye también el encargado autenticado en el contexto
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

def encargados(request):
    encargados = Encargado.objects.all()
    return render(request, 'encargado/encargado.html', {'encargados': encargados})

def agregar_encargado(request):
    pass
def editar_encargado(request):
    pass
def eliminar_encargado(request):
    pass