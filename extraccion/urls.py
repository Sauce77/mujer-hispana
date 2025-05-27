from django.urls import path
from . import views

app_name = 'extraccion' 

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear_extraccion, name="crear_extraccion")
]