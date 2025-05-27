from django.shortcuts import render

def index(request):
    """
    Vista para la página de inicio.
    """
    return render(request, 'core/index.html', {'nombre_proyecto': 'Mujer Hispana'})
