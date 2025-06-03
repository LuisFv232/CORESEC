from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json


@login_required
def dashboard(request):
    user = request.user
    context = {}

    # Importar modelos de forma segura
    try:
        from reportes.models import Informe, TipoInforme
        from notificaciones.models import Notificacion
    except ImportError:
        # Si los modelos no existen, crear datos por defecto
        context.update(get_default_dashboard_data(user))
        return render(request, 'dashboard/dashboard.html', context)

    if user.tipo_usuario in ['administrador', 'coordinador']:
        # Vista para administradores y coordinadores
        context.update(get_admin_dashboard_data(user))
    else:
        # Vista para usuarios municipales
        context.update(get_municipal_dashboard_data(user))

    # Actividad reciente común
    context['actividad_reciente'] = get_recent_activity(user)

    return render(request, 'dashboard/dashboard.html', context)


def get_default_dashboard_data(user):
    """Datos por defecto cuando los modelos no existen"""
    return {
        'total_informes': 0,
        'informes_pendientes': 0,
        'informes_revision': 0,
        'informes_atendidos': 0,
        'informes_observados': 0,
        'informes_aprobados': 0,
        'informes_rechazados': 0,
        'informes_requiere_correccion': 0,
        'mis_informes': 0,
        'mis_pendientes': 0,
        'mis_aprobados': 0,
        'mis_observados': 0,
        'mis_rechazados': 0,
        'mis_requiere_correccion': 0,
        'municipalidades_labels': json.dumps([]),
        'municipalidades_data': json.dumps([]),
        'tipos_labels': json.dumps([]),
        'tipos_data': json.dumps([]),
        'meses_labels': json.dumps([]),
        'meses_data': json.dumps([]),
        'user_type': user.tipo_usuario,
        'actividad_reciente': []
    }


def get_admin_dashboard_data(user):
    """Datos del dashboard para administradores y coordinadores"""
    try:
        from reportes.models import Informe, TipoInforme
        from usuarios.models import Usuario

        # Estadísticas generales por estado (usando los estados reales del modelo)
        total_informes = Informe.objects.count()
        informes_pendientes = Informe.objects.filter(estado='pendiente').count()
        informes_revision = Informe.objects.filter(estado='en_revision').count()
        informes_aprobados = Informe.objects.filter(estado='aprobado').count()
        informes_rechazados = Informe.objects.filter(estado='rechazado').count()
        informes_requiere_correccion = Informe.objects.filter(estado='requiere_correccion').count()

        # Datos para gráfica de municipalidades
        municipalidades_data = []
        municipalidades_labels = []

        for municipalidad_code, municipalidad_name in Usuario.MUNICIPALIDADES_HUANUCO:
            count = Informe.objects.filter(usuario__municipalidad=municipalidad_code).count()
            if count > 0:
                municipalidades_labels.append(municipalidad_name)
                municipalidades_data.append(count)

        # Datos para gráfica de tipos de informes (usando los tipos reales del modelo)
        tipos_data = []
        tipos_labels = []

        for tipo in TipoInforme.objects.filter(activo=True):
            count = Informe.objects.filter(tipo=tipo).count()
            if count > 0:
                tipos_labels.append(tipo.get_nombre_display())
                tipos_data.append(count)

        # Datos para gráfica de evolución mensual (últimos 6 meses)
        meses_labels = []
        meses_data = []

        for i in range(5, -1, -1):
            fecha = timezone.now() - timedelta(days=30 * i)
            mes_inicio = fecha.replace(day=1)
            if i == 0:
                mes_fin = timezone.now()
            else:
                mes_fin = (fecha.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            count = Informe.objects.filter(
                fecha_subida__gte=mes_inicio,
                fecha_subida__lte=mes_fin
            ).count()

            meses_labels.append(fecha.strftime('%b %Y'))
            meses_data.append(count)

        return {
            'total_informes': total_informes,
            'informes_pendientes': informes_pendientes,
            'informes_revision': informes_revision,
            'informes_aprobados': informes_aprobados,
            'informes_rechazados': informes_rechazados,
            'informes_requiere_correccion': informes_requiere_correccion,
            'municipalidades_labels': json.dumps(municipalidades_labels),
            'municipalidades_data': json.dumps(municipalidades_data),
            'tipos_labels': json.dumps(tipos_labels),
            'tipos_data': json.dumps(tipos_data),
            'meses_labels': json.dumps(meses_labels),
            'meses_data': json.dumps(meses_data),
            'user_type': 'admin',
        }
    except Exception as e:
        return get_default_dashboard_data(user)


def get_municipal_dashboard_data(user):
    """Datos del dashboard para usuarios municipales"""
    try:
        from reportes.models import Informe, TipoInforme

        # Estadísticas del usuario por estado
        mis_informes = Informe.objects.filter(usuario=user).count()
        mis_pendientes = Informe.objects.filter(usuario=user, estado='pendiente').count()
        mis_revision = Informe.objects.filter(usuario=user, estado='en_revision').count()
        mis_aprobados = Informe.objects.filter(usuario=user, estado='aprobado').count()
        mis_rechazados = Informe.objects.filter(usuario=user, estado='rechazado').count()
        mis_requiere_correccion = Informe.objects.filter(usuario=user, estado='requiere_correccion').count()

        # Datos para gráfica de tipos (solo los tipos que el usuario ha usado)
        tipos_data = []
        tipos_labels = []

        for tipo in TipoInforme.objects.filter(activo=True):
            count = Informe.objects.filter(usuario=user, tipo=tipo).count()
            if count > 0:
                tipos_labels.append(tipo.get_nombre_display())
                tipos_data.append(count)

        # Si no hay datos, mostrar todos los tipos disponibles con 0
        if not tipos_data:
            for tipo in TipoInforme.objects.filter(activo=True):
                if tipo.puede_acceder(user.tipo_usuario):
                    tipos_labels.append(tipo.get_nombre_display())
                    tipos_data.append(0)

        # Datos para gráfica de evolución mensual (últimos 6 meses)
        meses_labels = []
        meses_data = []

        for i in range(5, -1, -1):
            fecha = timezone.now() - timedelta(days=30 * i)
            mes_inicio = fecha.replace(day=1)
            if i == 0:
                mes_fin = timezone.now()
            else:
                mes_fin = (fecha.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            count = Informe.objects.filter(
                usuario=user,
                fecha_subida__gte=mes_inicio,
                fecha_subida__lte=mes_fin
            ).count()

            meses_labels.append(fecha.strftime('%b %Y'))
            meses_data.append(count)

        return {
            'mis_informes': mis_informes,
            'mis_pendientes': mis_pendientes,
            'mis_revision': mis_revision,
            'mis_aprobados': mis_aprobados,
            'mis_rechazados': mis_rechazados,
            'mis_requiere_correccion': mis_requiere_correccion,
            'tipos_labels': json.dumps(tipos_labels),
            'tipos_data': json.dumps(tipos_data),
            'meses_labels': json.dumps(meses_labels),
            'meses_data': json.dumps(meses_data),
            'user_type': 'municipal',
        }
    except Exception as e:
        return get_default_dashboard_data(user)


def get_recent_activity(user):
    """Actividad reciente del usuario"""
    actividad = []

    try:
        from reportes.models import Informe

        # Últimos informes del usuario
        if user.tipo_usuario == 'municipal':
            informes_recientes = Informe.objects.filter(usuario=user).order_by('-fecha_subida')[:5]
            for informe in informes_recientes:
                actividad.append({
                    'titulo': f'Informe subido: {informe.titulo}',
                    'descripcion': f'Estado: {informe.get_estado_display()} - {informe.tipo.get_nombre_display()}',
                    'fecha': informe.fecha_subida,
                    'tipo': 'informe',
                    'estado': informe.estado
                })
        else:
            # Para admin/coordinador, mostrar informes recientes de todas las municipalidades
            informes_recientes = Informe.objects.all().order_by('-fecha_subida')[:5]
            for informe in informes_recientes:
                actividad.append({
                    'titulo': f'Nuevo informe: {informe.titulo}',
                    'descripcion': f'De: {informe.usuario.get_municipalidad_display()} - {informe.tipo.get_nombre_display()}',
                    'fecha': informe.fecha_subida,
                    'tipo': 'informe',
                    'estado': informe.estado
                })
    except Exception as e:
        # Si hay error con los informes, mostrar actividad por defecto
        actividad = [
            {
                'titulo': 'Sistema iniciado',
                'descripcion': 'Dashboard cargado correctamente',
                'fecha': timezone.now(),
                'tipo': 'sistema',
                'estado': 'activo'
            }
        ]

    return actividad