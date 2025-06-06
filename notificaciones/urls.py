from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.notificaciones_view, name='notificaciones'),
]
