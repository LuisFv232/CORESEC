from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Informe, TipoInforme, RespuestaInforme
from .forms import InformeForm, RespuestaInformeForm

# Importaciones condicionales para evitar errores
try:
    from .utils import crear_notificacion_informe, obtener_tipos_informe_permitidos, validar_tipo_informe_usuario
except ImportError:
    # Funciones de respaldo si utils.py tiene problemas
    def crear_notificacion_informe(informe):
        pass


    def obtener_tipos_informe_permitidos(usuario):
        if usuario.tipo_usuario == 'municipal':
            return TipoInforme.objects.filter(nombre__in=['itca', 'ias'], activo=True)
        return TipoInforme.objects.filter(activo=True)


    def validar_tipo_informe_usuario(tipo_informe, usuario):
        return True, None


@login_required
def lista_informes(request):
    if request.user.tipo_usuario in ['administrador', 'coordinador']:
        # Administradores ven todos los informes
        informes = Informe.objects.all()
    else:
        # Usuarios municipales solo ven sus informes
        informes = Informe.objects.filter(usuario=request.user)

    # Filtros
    tipo_filtro = request.GET.get('tipo')
    estado_filtro = request.GET.get('estado')
    municipalidad_filtro = request.GET.get('municipalidad')
    año_filtro = request.GET.get('año')
    trimestre_filtro = request.GET.get('trimestre')
    buscar = request.GET.get('buscar')

    if tipo_filtro:
        informes = informes.filter(tipo_id=tipo_filtro)

    if estado_filtro:
        informes = informes.filter(estado=estado_filtro)

    if municipalidad_filtro and request.user.tipo_usuario in ['administrador', 'coordinador']:
        informes = informes.filter(usuario__municipalidad=municipalidad_filtro)

    if año_filtro:
        informes = informes.filter(año=año_filtro)

    if trimestre_filtro:
        informes = informes.filter(trimestre=trimestre_filtro)

    if buscar:
        informes = informes.filter(
            Q(titulo__icontains=buscar) |
            Q(descripcion__icontains=buscar)
        )

    # CORREGIDO: Ordenar por fecha_subida en lugar de fecha_creacion
    informes = informes.order_by('-fecha_subida')

    # Paginación
    paginator = Paginator(informes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Datos para filtros
    tipos_informe = obtener_tipos_informe_permitidos(request.user)
    años_disponibles = Informe.objects.values_list('año', flat=True).distinct().order_by('-año')

    # Importación condicional para evitar errores
    try:
        from usuarios.models import Usuario
        municipalidades = Usuario.MUNICIPALIDADES_HUANUCO if request.user.tipo_usuario in ['administrador',
                                                                                           'coordinador'] else []
    except (ImportError, AttributeError):
        municipalidades = []

    context = {
        'informes': page_obj,
        'tipos_informe': tipos_informe,
        'años_disponibles': años_disponibles,
        'municipalidades': municipalidades,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }

    return render(request, 'reportes/lista_informes.html', context)


@login_required
def crear_informe(request):
    if request.method == 'POST':
        form = InformeForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            informe = form.save(commit=False)
            informe.usuario = request.user

            # Validar tipo de informe según usuario
            es_valido, mensaje_error = validar_tipo_informe_usuario(informe.tipo, request.user)
            if not es_valido:
                messages.error(request, mensaje_error)
                return render(request, 'reportes/crear_informe.html', {'form': form})

            informe.save()

            # Crear notificación automática
            try:
                crear_notificacion_informe(informe)
            except Exception as e:
                # Si falla la notificación, continuar sin error
                pass

            messages.success(request, f'Informe {informe.tipo.get_nombre_display()} creado exitosamente.')
            return redirect('reportes:lista_informes')
    else:
        form = InformeForm(user=request.user)

    # Información contextual para el usuario
    context = {
        'form': form,
        'tipos_info': {
            'itca': 'Solo para usuarios municipales. Requiere trimestre y año.',
            'ficha_verificacion': 'Solo para administradores y coordinadores. Requiere fecha específica.',
            'supervisiones': 'Solo para administradores y coordinadores. Requiere fecha específica.',
            'its': 'Solo para administradores y coordinadores. Debe responder a un informe ITCA.',
            'ias': 'Para todos los usuarios. Solo requiere año.',
        }
    }

    return render(request, 'reportes/crear_informe.html', context)


@login_required
def detalle_informe(request, informe_id):
    if request.user.tipo_usuario in ['administrador', 'coordinador']:
        informe = get_object_or_404(Informe, id=informe_id)
    else:
        informe = get_object_or_404(Informe, id=informe_id, usuario=request.user)

    respuestas = RespuestaInforme.objects.filter(informe=informe).order_by('-fecha_respuesta')

    context = {
        'informe': informe,
        'respuestas': respuestas,
    }

    return render(request, 'reportes/detalle_informe.html', context)


# views.py - Vista responder_informe mejorada

@login_required
@login_required
def responder_informe(request, informe_id):
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para responder informes.')
        return redirect('reportes:lista_informes')

    informe = get_object_or_404(Informe, id=informe_id)

    if request.method == 'POST':
        form = RespuestaInformeForm(request.POST, request.FILES, informe=informe)
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.informe = informe
            respuesta.usuario = request.user

            try:
                # Generar nombre de archivo estructurado
                if respuesta.archivo_adjunto:
                    # Obtener la extensión del archivo original
                    nombre_original = respuesta.archivo_adjunto.name
                    nombre_base, extension = os.path.splitext(nombre_original)

                    # Generar nuevo nombre con estructura
                    fecha_respuesta = timezone.now().strftime('%Y%m%d_%H%M%S')
                    nuevo_nombre = f"RESP_{informe.tipo.nombre.upper()}_{informe.id}_{fecha_respuesta}{extension}"

                    # Asignar el nuevo nombre al archivo
                    respuesta.archivo_adjunto.name = upload_respuesta_to_structured_path(
                        respuesta, nuevo_nombre
                    )

                respuesta.save()

                # Actualizar estado del informe si se especifica
                nuevo_estado = request.POST.get('nuevo_estado')
                if nuevo_estado and nuevo_estado in ['en_revision', 'aprobado', 'rechazado', 'requiere_correccion']:
                    informe.estado = nuevo_estado
                    informe.fecha_actualizacion = timezone.now()
                    informe.save()

                messages.success(request,
                                 f'Respuesta enviada exitosamente como {respuesta.tipo_documento.get_nombre_display()}.')
                return redirect('reportes:detalle_informe', informe_id=informe.id)

            except Exception as e:
                messages.error(request, f'Error al guardar la respuesta: {str(e)}')
                logger.error(f"Error al responder informe {informe_id}: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = RespuestaInformeForm(informe=informe)

    context = {
        'form': form,
        'informe': informe,
    }
    return render(request, 'reportes/responder_informe.html', context)
@login_required
def cambiar_estado_informe(request, informe_id):
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    if request.method == 'POST':
        informe = get_object_or_404(Informe, id=informe_id)
        nuevo_estado = request.POST.get('estado')

        # CORREGIDO: Usar los estados que están definidos en el modelo
        if nuevo_estado in ['pendiente', 'en_revision', 'aprobado', 'rechazado', 'requiere_correccion']:
            informe.estado = nuevo_estado
            # Solo actualizar fecha_actualizacion que existe en el modelo
            informe.fecha_actualizacion = timezone.now()
            informe.save()

            return JsonResponse({'success': True, 'nuevo_estado': informe.get_estado_display()})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vistas adicionales para compatibilidad con templates existentes
@login_required
def lista_reportes(request):
    """Vista de compatibilidad que redirige a lista_informes"""
    return redirect('reportes:lista_informes')


@login_required
def crear_reporte(request):
    """Vista de compatibilidad que redirige a crear_informe"""
    return redirect('reportes:crear_informe')


@login_required
def detalle_reporte(request, reporte_id):
    """Vista de compatibilidad que redirige a detalle_informe"""
    return redirect('reportes:detalle_informe', informe_id=reporte_id)
