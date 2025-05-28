from django.shortcuts import render, HttpResponse, get_object_or_404
import datetime
import plotly.express as px
from plotly.offline import plot
import pandas as pd

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

def mostrar_dashboard(request):
    """
        Muestra graficas sobre las cuentas por cobrar.
    """

    form = DateFilterForm(request.GET)

    id_extraccion = request.session.get("id_extraccion")

    if not id_extraccion:
        extraccion_reciente = Extraccion.objects.order_by('-fecha_creacion').first()
        id_extraccion = extraccion_reciente.id


    extraccion = get_object_or_404(Extraccion, pk=id_extraccion)

    registros = extraccion.registro_set.all()

    # convertimos a un dataframe

    registros_list = list(registros.values())

    df = pd.DataFrame(registros_list)
    df['total'] = df['total'].astype(float)
    df['abonado'] = df['abonado'].astype(float)
    df['debe'] = df['debe'].astype(float)

    # Calcular el saldo pendiente
    df['pendiente'] = df['total'] - df['abonado']

    # Convertir fecha_vencimiento a datetime y calcular días hasta vencimiento
    df['fecha_vencimiento'] = pd.to_datetime(df['fecha_vencimiento'])
    df['dias_hasta_vencimiento'] = (df['fecha_vencimiento'] - pd.Timestamp.now()).dt.days

    # --- GRÁFICO 1: Saldo Pendiente por Proveedor (Barras) ---
    df_tienda_pendiente = df.groupby('tienda')['pendiente'].sum().reset_index()
    fig1 = px.bar(df_tienda_pendiente,
                  x='tienda',
                  y='pendiente',
                  title='Saldo Pendiente por Tienda',
                  labels={'tienda': 'Tienda', 'pendiente': 'Monto Pendiente ($)'},
                  color='tienda' # Colorear por proveedor
    )
    plot_div1 = plot(fig1, output_type='div', include_plotlyjs='cdn', auto_open=False)

    # --- GRÁFICO 2: Distribución del Total Original (Pastel) ---
    fig2 = px.pie(df,
                  names='tienda',
                  values='total',
                  title='Distribución del Total Original de Deuda por Tienda',
                  hole=0.3 # Gráfico de dona
    )
    plot_div2 = plot(fig2, output_type='div', include_plotlyjs='cdn', auto_open=False)

    # --- GRÁFICO 3: Cuentas Pendientes por Vencimiento (Dispersión) ---
    # Filtrar solo las cuentas con saldo pendiente
    df_pendientes = df[df['pendiente'] > 0]
    fig3 = px.scatter(df_pendientes,
                      x='dias_hasta_vencimiento',
                      y='pendiente',
                      size='total', # El tamaño de la burbuja es el total original
                      color='tienda', # Colorear por proveedor
                      hover_name='nombre', # Mostrar ID de cuenta al pasar el ratón
                      title='Cuentas por Cobrar: Días hasta Vencimiento vs. Saldo',
                      labels={'dias_hasta_vencimiento': 'Días hasta Vencimiento (positivo = futuro, negativo = vencido)',
                              'pendiente': 'Saldo Pendiente ($)'},
                      text='nombre' # Mostrar ID de cuenta en el gráfico
    )
    # Ajustar el texto para que se vea mejor (opcional)
    fig3.update_traces(textposition='top center')
    fig3.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    plot_div3 = plot(fig3, output_type='div', include_plotlyjs='cdn', auto_open=False)


    context = {
        'chart1_html': plot_div1, # Renombré las variables para mayor claridad
        'chart2_html': plot_div2,
        'chart3_html': plot_div3,
        'page_title': 'Dashboard de Cuentas por Cobrar'
    }

    return render(request, 'dashboard/dashboards.html', context)