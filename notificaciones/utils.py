from .models import Notificacion

def crear_notificacion(usuario, titulo, mensaje, tipo='info'):
    """
    Crea una nueva notificación para un usuario.
    
    Args:
        usuario: El usuario que recibirá la notificación
        titulo: Título de la notificación
        mensaje: Mensaje de la notificación
        tipo: Tipo de notificación ('info', 'success', 'warning', 'error')
    """
    notificacion = Notificacion.objects.create(
        usuario=usuario,
        titulo=titulo,
        mensaje=mensaje,
        tipo=tipo
    )
    return notificacion

def obtener_notificaciones_no_leidas(usuario):
    """
    Obtiene las notificaciones no leídas de un usuario.
    
    Args:
        usuario: El usuario del cual obtener las notificaciones
        
    Returns:
        QuerySet de notificaciones no leídas
    """
    return Notificacion.objects.filter(usuario=usuario, leida=False).order_by('-fecha_creacion')
