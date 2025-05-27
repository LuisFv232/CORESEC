from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from notificaciones.models import Notificacion

def enviar_notificacion_cambio_estado(informe, nuevo_estado, usuario_que_cambia):
    """Enviar notificación por email cuando cambia el estado de un informe"""
    
    # Crear notificación en el sistema
    Notificacion.objects.create(
        usuario=informe.usuario,
        titulo=f'Estado de informe actualizado: {informe.titulo}',
        mensaje=f'Tu informe "{informe.titulo}" ha cambiado de estado a: {informe.get_estado_display()}. Revisado por: {usuario_que_cambia.get_full_name()}',
        tipo='info' if nuevo_estado in ['en_revision', 'atendido'] else 'warning' if nuevo_estado == 'observado' else 'success',
        enlace=f'/reportes/{informe.id}/'
    )
    
    # Enviar email si está configurado
    if hasattr(settings, 'EMAIL_HOST') and informe.usuario.email:
        contexto = {
            'informe': informe,
            'nuevo_estado': nuevo_estado,
            'usuario_que_cambia': usuario_que_cambia,
            'usuario_destinatario': informe.usuario
        }
        
        asunto = f'CORESEC - Estado de informe actualizado: {informe.titulo}'
        mensaje_html = render_to_string('emails/cambio_estado_informe.html', contexto)
        
        try:
            send_mail(
                asunto,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [informe.usuario.email],
                html_message=mensaje_html,
                fail_silently=True
            )
        except Exception as e:
            print(f"Error enviando email: {e}")

def enviar_notificacion_nuevo_informe(informe):
    """Notificar a administradores cuando se sube un nuevo informe"""
    from usuarios.models import Usuario
    
    administradores = Usuario.objects.filter(tipo_usuario__in=['administrador', 'coordinador'])
    
    for admin in administradores:
        Notificacion.objects.create(
            usuario=admin,
            titulo=f'Nuevo informe recibido: {informe.titulo}',
            mensaje=f'Se ha subido un nuevo informe desde {informe.usuario.get_municipalidad_display()}: "{informe.titulo}" por {informe.usuario.get_full_name()}',
            tipo='info',
            enlace=f'/reportes/{informe.id}/'
        )
