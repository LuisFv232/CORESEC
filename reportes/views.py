from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Informe, TipoInforme, RespuestaInforme, TipoDocumentoRespuesta
from .forms import InformeForm, RespuestaInformeForm, TipoInformeForm, TipoDocumentoRespuestaForm
from usuarios.models import Usuario
import logging

logger = logging.getLogger(__name__)


@login_required
def lista_informes(request):
    if request.user.tipo_usuario in ['administrador', 'coordinador']:
        informes = Informe.objects.all()
    else:
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

    informes = informes.order_by('-fecha_subida')
    paginator = Paginator(informes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'informes': page_obj,
        'tipos_informe': TipoInforme.objects.filter(activo=True),
        'años_disponibles': Informe.objects.values_list('año', flat=True).distinct().order_by('-año'),
        'municipalidades': Usuario.MUNICIPALIDADES_HUANUCO if request.user.tipo_usuario in ['administrador',
                                                                                            'coordinador'] else [],
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }

    return render(request, 'reportes/lista_informes.html', context)


@login_required
def crear_informe(request):
    if not hasattr(request.user, 'municipalidad') and request.user.tipo_usuario == 'municipal':
        messages.error(request, 'No tiene una municipalidad asignada. Contacte al administrador.')
        return redirect('reportes:lista_informes')

    if request.method == 'POST':
        form = InformeForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            informe = form.save(commit=False)
            informe.usuario = request.user
            informe.municipalidad = request.user.municipalidad
            informe.save()
            messages.success(request, 'Informe subido exitosamente!')
            return redirect('reportes:lista_informes')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = InformeForm(user=request.user)

        # Verificar si hay tipos disponibles
        if not form.fields['tipo'].queryset.exists():
            messages.warning(request,
                             'No hay tipos de informe disponibles para su perfil. Contacte al administrador.')
            return redirect('reportes:lista_informes')

    context = {
        'form': form,
        'titulo_pagina': 'Subir Nuevo Informe'
    }
    return render(request, 'reportes/crear_informe.html', context)
@login_required
def detalle_informe(request, pk):
    if request.user.tipo_usuario in ['administrador', 'coordinador']:
        informe = get_object_or_404(Informe, pk=pk)
    else:
        informe = get_object_or_404(Informe, pk=pk, usuario=request.user)

    respuestas = RespuestaInforme.objects.filter(informe=informe).order_by('-fecha_respuesta')

    context = {
        'informe': informe,
        'respuestas': respuestas,
    }
    return render(request, 'reportes/detalle_informe.html', context)


@login_required
@permission_required('reportes.add_respuestainforme')
def responder_informe(request, pk):
    informe = get_object_or_404(Informe, pk=pk)

    if request.method == 'POST':
        form = RespuestaInformeForm(request.POST, request.FILES, informe=informe)
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.informe = informe
            respuesta.usuario = request.user

            try:
                respuesta.save()

                # Actualizar estado del informe si se especifica
                nuevo_estado = request.POST.get('nuevo_estado')
                if nuevo_estado in ['en_revision', 'aprobado', 'rechazado', 'requiere_correccion']:
                    informe.estado = nuevo_estado
                    informe.save()

                messages.success(request, 'Respuesta enviada exitosamente!')
                return redirect('reportes:detalle_informe', pk=informe.pk)
            except Exception as e:
                logger.error(f"Error al responder informe {pk}: {str(e)}")
                messages.error(request, 'Ocurrió un error al guardar la respuesta.')
    else:
        form = RespuestaInformeForm(informe=informe)

    context = {
        'form': form,
        'informe': informe,
    }
    return render(request, 'reportes/responder_informe.html', context)


@login_required
@permission_required('reportes.change_informe')
def cambiar_estado_informe(request, pk):
    if request.method == 'POST':
        informe = get_object_or_404(Informe, pk=pk)
        nuevo_estado = request.POST.get('estado')

        if nuevo_estado in ['pendiente', 'en_revision', 'aprobado', 'rechazado', 'requiere_correccion']:
            informe.estado = nuevo_estado
            informe.save()
            return JsonResponse({'success': True, 'nuevo_estado': informe.get_estado_display()})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Gestión de Tipos de Informe
@login_required
@permission_required('reportes.view_tipoinforme')
def lista_tipos_informe(request):
    tipos = TipoInforme.objects.all().order_by('nombre')
    return render(request, 'reportes/admin/tipos_informe/lista.html', {'tipos': tipos})


@login_required
@permission_required('reportes.add_tipoinforme')
def crear_tipo_informe(request):
    if request.method == 'POST':
        form = TipoInformeForm(request.POST)
        if form.is_valid():
            tipo = form.save()

            # Crear estructura de carpetas para todas las municipalidades
            for codigo, nombre in Usuario.MUNICIPALIDADES_HUANUCO:
                tipo.crear_estructura(codigo)

            messages.success(request, f'Tipo de informe "{tipo.nombre_display}" creado exitosamente!')
            return redirect('reportes:lista_tipos_informe')
    else:
        form = TipoInformeForm()

    return render(request, 'reportes/admin/tipos_informe/crear.html', {'form': form})


@login_required
@permission_required('reportes.change_tipoinforme')
def editar_tipo_informe(request, pk):
    tipo = get_object_or_404(TipoInforme, pk=pk)

    if request.method == 'POST':
        form = TipoInformeForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada correctamente')
            return redirect('reportes:lista_tipos_informe')
    else:
        form = TipoInformeForm(instance=tipo)

    return render(request, 'reportes/admin/tipos_informe/editar.html', {'form': form, 'tipo': tipo})


# Gestión de Tipos de Documento
@login_required
@permission_required('reportes.view_tipodocumentorespuesta')
def lista_tipos_documento(request):
    tipos = TipoDocumentoRespuesta.objects.all().order_by('nombre')
    return render(request, 'reportes/admin/tipos_documento/lista.html', {'tipos': tipos})


@login_required
@permission_required('reportes.add_tipodocumentorespuesta')
def crear_tipo_documento(request):
    if request.method == 'POST':
        form = TipoDocumentoRespuestaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de documento creado exitosamente!')
            return redirect('reportes:lista_tipos_documento')
    else:
        form = TipoDocumentoRespuestaForm()

    return render(request, 'reportes/admin/tipos_documento/crear.html', {'form': form})


@login_required
@permission_required('reportes.change_tipodocumentorespuesta')
def editar_tipo_documento(request, pk):
    tipo = get_object_or_404(TipoDocumentoRespuesta, pk=pk)

    if request.method == 'POST':
        form = TipoDocumentoRespuestaForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada correctamente')
            return redirect('reportes:lista_tipos_documento')
    else:
        form = TipoDocumentoRespuestaForm(instance=tipo)

    return render(request, 'reportes/admin/tipos_documento/editar.html', {'form': form, 'tipo': tipo})

