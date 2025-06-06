from django.contrib.auth import get_user_model
from notificaciones.models import Notificacion

User = get_user_model()

def crear_notificacion_informe(informe):
    """
    Crea notificaciones automáticas cuando se sube un nuevo informe
    """
    # Notificar a administradores y coordinadores
    usuarios_notificar = User.objects.filter(
        tipo_usuario__in=['administrador', 'coordinador']
    )
    
    for usuario in usuarios_notificar:
        Notificacion.objects.create(
            usuario=usuario,
            titulo=f'Nuevo informe {informe.tipo.get_nombre_display()}',
            mensaje=f'Se ha subido un nuevo informe de tipo {informe.tipo.get_nombre_display()} por {informe.usuario.get_full_name() or informe.usuario.username}',
            tipo='info',
            leida=False
        )

def obtener_tipos_informe_permitidos(usuario):
    """
    Retorna los tipos de informe que puede crear un usuario según su rol
    """
    from .models import TipoInforme
    
    if usuario.tipo_usuario == 'municipal':
        # Usuarios municipales solo pueden crear ITCA e IAS
        return TipoInforme.objects.filter(nombre__in=['itca', 'ias'], activo=True)
    elif usuario.tipo_usuario in ['administrador', 'coordinador']:
        # Administradores y coordinadores pueden crear todos los tipos
        return TipoInforme.objects.filter(activo=True)
    else:
        # Por defecto, solo IAS
        return TipoInforme.objects.filter(nombre='ias', activo=True)

def validar_tipo_informe_usuario(tipo_informe, usuario):
    """
    Valida si un usuario puede crear un tipo específico de informe
    """
    if tipo_informe.nombre == 'itca' and usuario.tipo_usuario != 'municipal':
        return False, 'Solo los usuarios municipales pueden crear informes ITCA.'
    
    if tipo_informe.nombre in ['ficha_verificacion', 'supervisiones', 'its'] and usuario.tipo_usuario not in ['administrador', 'coordinador']:
        return False, f'Solo los administradores y coordinadores pueden crear informes {tipo_informe.get_nombre_display()}.'
    
    return True, None

def generar_ruta_archivo(informe):
    """
    Genera la ruta donde se guardará el archivo del informe
    """
    municipalidad = informe.usuario.municipalidad
    tipo = informe.tipo.get_nombre_display()
    año = informe.año
    
    if informe.tipo.nombre == 'itca':
        trimestre = informe.get_trimestre_display()
        return f'INFORMES/{municipalidad}/{tipo}/{año}/{trimestre}/'
    elif informe.tipo.nombre in ['ficha_verificacion', 'supervisiones']:
        fecha = informe.fecha_especifica.strftime('%Y-%m-%d') if informe.fecha_especifica else 'sin_fecha'
        return f'INFORMES/{municipalidad}/{tipo}/{año}/{fecha}/'
    elif informe.tipo.nombre == 'its':
        # Para ITS, usar la información del informe padre (ITCA)
        if informe.informe_padre:
            trimestre = informe.informe_padre.get_trimestre_display()
            return f'INFORMES/{municipalidad}/{tipo}/{año}/{trimestre}/'
        else:
            return f'INFORMES/{municipalidad}/{tipo}/{año}/'
    else:  # IAS
        return f'INFORMES/{municipalidad}/{tipo}/{año}/'
