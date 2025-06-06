from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Informes
    path('', views.lista_informes, name='lista_informes'),
    path('crear/', views.crear_informe, name='crear_informe'),
    path('<int:pk>/', views.detalle_informe, name='detalle_informe'),
    path('<int:pk>/responder/', views.responder_informe, name='responder_informe'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_informe, name='cambiar_estado_informe'),

    # Tipos de Informe
    path('admin/tipos-informe/', views.lista_tipos_informe, name='lista_tipos_informe'),
    path('admin/tipos-informe/crear/', views.crear_tipo_informe, name='crear_tipo_informe'),
    path('admin/tipos-informe/editar/<int:pk>/', views.editar_tipo_informe, name='editar_tipo_informe'),

    # Tipos de Documento
    path('admin/tipos-documento/', views.lista_tipos_documento, name='lista_tipos_documento'),
    path('admin/tipos-documento/crear/', views.crear_tipo_documento, name='crear_tipo_documento'),
    path('admin/tipos-documento/editar/<int:pk>/', views.editar_tipo_documento, name='editar_tipo_documento'),
]