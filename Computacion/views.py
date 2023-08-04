from django.shortcuts import render, redirect
from .models import Encargado
from django.contrib import messages

# Create your views here.
def login (request):
    return render(request, 'login/login.html')

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
            return render(request, 'login/login.html')

        # Comparar la contraseña ingresada con la contraseña almacenada en el modelo
        if encargado.contrasenia == contrasenia:
            # Redirigir a otra página o hacer cualquier otra acción, cuardamos el id del empleado
            # Y lo mandamos a la otra ruta
            request.session['encargado_id'] = encargado.id
            return redirect('acceso')  # Aquí 'acceso' es el nombre de la URL a la que deseas
        else:
            # Las credenciales son inválidas, mostrar un mensaje de error
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'login/login.html')

    # Si no es una solicitud POST, renderizar el formulario de inicio de sesión
    return render(request, 'login/login.html')

def acceso(request):
    return render(request, 'adminlte/index.html')

def qr_reader_view(request):
    return render(request, 'qr/qr_reader.html')