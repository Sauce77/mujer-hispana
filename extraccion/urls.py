from django.urls import path
from . import views

app_name = 'extraccion' 

urlpatterns = [
    path('', views.mostrar_extracciones, name="mostrar_extracciones"),
    path('crear/', views.crear_extraccion, name="crear_extraccion"),
    path('obtener/<int:extraccion_id>/', views.obtener_extraccion, name="obtener_extraccion"),
]