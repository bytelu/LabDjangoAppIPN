from django.shortcuts import render, redirect
from .models import Encargado
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

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

        # Comparar la contraseña ingresada con el hash almacenado en el modelo
        if check_password(contrasenia, encargado.contrasenia):
            # Redirigir a otra página o hacer cualquier otra acción, guardamos el id del empleado
            # Y lo mandamos a la otra ruta
            request.session['encargado_id'] = encargado.id
            return redirect('acceso')  # Aquí 'acceso' es el nombre de la URL a la que deseas redirigir
        else:
            # Las credenciales son inválidas, mostrar un mensaje de error
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('login')

    # Si no es una solicitud POST, renderizar el formulario de inicio de sesión
    return redirect('login')


def acceso(request):
    return render(request, 'adminlte/index.html')

def registro(request):
    if request.method == 'POST':
        username = request.POST.get('usuario', '')
        password = request.POST.get('contrasenia', '')
        confirm_password = request.POST.get('contraseniados', '')
        nombre = request.POST.get('nombre', '')
        apellido_p = request.POST.get('apellido_p', '')
        apellido_m = request.POST.get('apellido_m', '')

        if password == confirm_password:
            # Genera la contraseña segura utilizando make_password()
            hashed_password = make_password(password)

            # Crea el encargado con la contraseña segura
            encargado = Encargado(
                usuario=username,
                contrasenia=hashed_password,
                nombre=nombre,
                apellido_m=apellido_m,
                apellido_p=apellido_p
            )
            encargado.save()

            # Redirecciona al usuario a la página de inicio de sesión con mensaje de éxito
            messages.success(request, "Usuario registrado correctamente.")
            return render(request, 'login/login.html', {'es_registro': True})

        else:
            # Si las contraseñas no coinciden, muestra un mensaje de error en el formulario
            messages.error(request, "Las contraseñas no coinciden.")
            # Redirecciona al usuario al formulario de registro, pero mantén los datos de usuario ingresados
            # y borra solo las contraseñas para que pueda volver a ingresarlas.
            return render(request, 'login/login.html', {'es_registro': True})

    # Si el método de solicitud es GET o hay algún otro error, muestra el formulario de registro
    # sin datos ingresados, para que el usuario pueda comenzar a registrarse.
    return render(request, 'login/login.html', {'es_registro': True})

def crearsesion_indiv(request):
    return render(request, 'interfazencargado/individual.html')

def crearsesion_grupal(request):
    return render(request, 'interfazencargado/grupo.html')
