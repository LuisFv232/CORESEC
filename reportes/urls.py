from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.lista_informes, name='lista_informes'),
    path('crear/', views.crear_informe, name='crear_informe'),
    path('<int:informe_id>/', views.detalle_informe, name='detalle_informe'),
    path('<int:informe_id>/responder/', views.responder_informe, name='responder_informe'),
    path('<int:informe_id>/cambiar-estado/', views.cambiar_estado_informe, name='cambiar_estado_informe'),
]
