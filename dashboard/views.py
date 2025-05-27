from django.shortcuts import render, HttpResponse, get_object_or_404
import datetime

from extraccion.models import Extraccion
from .forms import DateFilterForm
# Create your views here.

def index(request):
    return HttpResponse("Dashboards")

def tabla_registros(request):
    """
        Muestra los registros de una extraccion.
    """

    form = DateFilterForm(request.GET)

    id_extraccion = request.session.get("id_extraccion")

    if not id_extraccion:
        extraccion_reciente = Extraccion.objects.order_by('-fecha_creacion').first()
        id_extraccion = extraccion_reciente.id


    extraccion = get_object_or_404(Extraccion, pk=id_extraccion)

    registros = extraccion.registro_set.all()

    if form.is_valid():
        fecha_inicio = form.cleaned_data.get('start_date')
        fecha_fin = form.cleaned_data.get('end_date')

        if fecha_inicio:
            # Filtrar objetos donde la fecha sea mayor o igual que la fecha de inicio
            registros = registros.filter(fecha_vencimiento__gte=fecha_inicio)

        if fecha_fin:
            # Filtrar objetos donde la fecha sea menor o igual que la fecha de fin
            queryset = queryset.filter(fecha_vencimiento__lte=fecha_fin)

    context = {
        'form': form,
        'datos': registros,
    }

    return render(request, "dashboard/tabla.html", context)

    