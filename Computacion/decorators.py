from functools import wraps
from django.shortcuts import redirect

def encargado_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if 'encargado_id' not in request.session:
            # Si el encargado no está autenticado, redireccionar a la página de error
            return redirect('pagina_error')
        return view_func(request, *args, **kwargs)
    return wrapped_view