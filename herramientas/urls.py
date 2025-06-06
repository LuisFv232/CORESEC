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

    path('tipos-informes/', views.gestion_tipos_informes, name='gestion_tipos_informes'),
    path('tipos-informes/crear/', views.crear_tipo_informe, name='crear_tipo_informe'),
    path('tipos-informes/<int:tipo_id>/editar/', views.editar_tipo_informe, name='editar_tipo_informe'),
    path('tipos-informes/<int:tipo_id>/eliminar/', views.eliminar_tipo_informe, name='eliminar_tipo_informe'),
    path('tipos-informes/<int:tipo_id>/toggle-estado/', views.toggle_estado_tipo_informe,
         name='toggle_estado_tipo_informe'),
]