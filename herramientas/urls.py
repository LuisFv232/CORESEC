from django.urls import path
from . import views

app_name = 'herramientas'

urlpatterns = [
    path('', views.herramientas, name='herramientas'),
    path('documentos/', views.gestion_documentos, name='gestion_documentos'),
    path('documentos/subir/', views.subir_documento, name='subir_documento'),
    path('carpetas/', views.organizar_carpetas, name='organizar_carpetas'),
    path('explorador/', views.explorador_archivos, name='explorador_archivos'),
    path('informacion/', views.gestion_informacion, name='gestion_informacion'),
    path('recursos/', views.documentos_recursos, name='documentos_recursos'),
    path('tipos-documento/', views.lista_tipos_documento, name='lista_tipos_documento'),
    path('tipos-documento/crear/', views.crear_tipo_documento, name='crear_tipo_documento'),
    path('tipos-documento/editar/<int:pk>/', views.editar_tipo_documento, name='editar_tipo_documento'),
]
