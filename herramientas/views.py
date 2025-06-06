from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Documento, Enlace, RecursoConasec
from .forms import DocumentoForm, EnlaceForm
# Importar modelo TipoInforme desde reportes
from reportes.models import TipoInforme
import os
from django.conf import settings
from datetime import datetime, date


@login_required
def herramientas(request):
    # Solo administradores y coordinadores pueden acceder
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:dashboard')

    # Documentos recientes
    documentos_recientes = Documento.objects.filter(activo=True).order_by('-fecha_subida')[:5]

    # Enlaces por categoría
    enlaces_institucionales = Enlace.objects.filter(categoria='institucional', activo=True)
    enlaces_academicos = Enlace.objects.filter(categoria='academico', activo=True)
    enlaces_soporte = Enlace.objects.filter(categoria='soporte', activo=True)

    # Estadísticas de tipos de informes
    total_tipos_informe = TipoInforme.objects.filter(activo=True).count()

    context = {
        'documentos_recientes': documentos_recientes,
        'enlaces_institucionales': enlaces_institucionales,
        'enlaces_academicos': enlaces_academicos,
        'enlaces_soporte': enlaces_soporte,
        'total_tipos_informe': total_tipos_informe,
    }

    return render(request, 'herramientas/herramientas.html', context)


@login_required
def gestion_tipos_informes(request):
    """Vista para gestionar tipos de informes"""
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para gestionar tipos de informes.')
        return redirect('dashboard:dashboard')

    tipos_informes = TipoInforme.objects.all()

    # Filtros
    activo_filtro = request.GET.get('activo')
    buscar = request.GET.get('buscar')

    if activo_filtro:
        activo_bool = activo_filtro.lower() == 'true'
        tipos_informes = tipos_informes.filter(activo=activo_bool)

    if buscar:
        tipos_informes = tipos_informes.filter(
            Q(nombre__icontains=buscar) |
            Q(descripcion__icontains=buscar)
        )

    # Ordenar por fecha de creación descendente
    tipos_informes = tipos_informes.order_by('-fecha_creacion')

    # Paginación
    paginator = Paginator(tipos_informes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tipos_informes': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }

    return render(request, 'herramientas/gestion_tipos_informes.html', context)


@login_required
def crear_tipo_informe(request):
    """Vista para crear un nuevo tipo de informe"""
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para crear tipos de informes.')
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        requiere_periodo = request.POST.get('requiere_periodo') == 'on'
        activo = request.POST.get('activo') == 'on'
        permite_municipal = request.POST.get('permite_municipal') == 'on'
        permite_admin = request.POST.get('permite_admin') == 'on'
        permite_coordinador = request.POST.get('permite_coordinador') == 'on'

        # Validaciones
        if not nombre or not descripcion:
            messages.error(request, 'El nombre y la descripción son obligatorios.')
            return render(request, 'herramientas/crear_tipo_informe.html')

        # Verificar que el nombre no exista
        if TipoInforme.objects.filter(nombre=nombre).exists():
            messages.error(request, 'Ya existe un tipo de informe con ese nombre.')
            return render(request, 'herramientas/crear_tipo_informe.html')

        # Crear el tipo de informe
        tipo_informe = TipoInforme.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            requiere_periodo=requiere_periodo,
            activo=activo,
            permite_municipal=permite_municipal,
            permite_admin=permite_admin,
            permite_coordinador=permite_coordinador
        )

        messages.success(request, f'Tipo de informe "{tipo_informe.get_nombre_display()}" creado exitosamente.')
        return redirect('herramientas:gestion_tipos_informes')

    # Obtener choices disponibles para el template
    tipos_choices = TipoInforme.TIPOS_CHOICES

    context = {
        'tipos_choices': tipos_choices,
    }

    return render(request, 'herramientas/crear_tipo_informe.html', context)


@login_required
def editar_tipo_informe(request, tipo_id):
    """Vista para editar un tipo de informe existente"""
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para editar tipos de informes.')
        return redirect('dashboard:dashboard')

    tipo_informe = get_object_or_404(TipoInforme, id=tipo_id)

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        requiere_periodo = request.POST.get('requiere_periodo') == 'on'
        activo = request.POST.get('activo') == 'on'
        permite_municipal = request.POST.get('permite_municipal') == 'on'
        permite_admin = request.POST.get('permite_admin') == 'on'
        permite_coordinador = request.POST.get('permite_coordinador') == 'on'

        # Validaciones
        if not nombre or not descripcion:
            messages.error(request, 'El nombre y la descripción son obligatorios.')
            return render(request, 'herramientas/editar_tipo_informe.html', {'tipo_informe': tipo_informe})

        # Verificar que el nombre no exista en otros registros
        if TipoInforme.objects.filter(nombre=nombre).exclude(id=tipo_id).exists():
            messages.error(request, 'Ya existe otro tipo de informe con ese nombre.')
            return render(request, 'herramientas/editar_tipo_informe.html', {'tipo_informe': tipo_informe})

        # Actualizar el tipo de informe
        tipo_informe.nombre = nombre
        tipo_informe.descripcion = descripcion
        tipo_informe.requiere_periodo = requiere_periodo
        tipo_informe.activo = activo
        tipo_informe.permite_municipal = permite_municipal
        tipo_informe.permite_admin = permite_admin
        tipo_informe.permite_coordinador = permite_coordinador
        tipo_informe.save()

        messages.success(request, f'Tipo de informe "{tipo_informe.get_nombre_display()}" actualizado exitosamente.')
        return redirect('herramientas:gestion_tipos_informes')

    # Obtener choices disponibles para el template
    tipos_choices = TipoInforme.TIPOS_CHOICES

    context = {
        'tipo_informe': tipo_informe,
        'tipos_choices': tipos_choices,
    }

    return render(request, 'herramientas/editar_tipo_informe.html', context)


@login_required
def eliminar_tipo_informe(request, tipo_id):
    """Vista para eliminar un tipo de informe"""
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    if request.method == 'POST':
        tipo_informe = get_object_or_404(TipoInforme, id=tipo_id)

        # Verificar si hay informes asociados
        if tipo_informe.informe_set.exists():
            return JsonResponse({
                'error': 'No se puede eliminar este tipo de informe porque tiene informes asociados.'
            }, status=400)

        nombre_tipo = tipo_informe.get_nombre_display()
        tipo_informe.delete()

        return JsonResponse({
            'success': True,
            'message': f'Tipo de informe "{nombre_tipo}" eliminado exitosamente.'
        })

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def toggle_estado_tipo_informe(request, tipo_id):
    """Vista para activar/desactivar un tipo de informe"""
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    if request.method == 'POST':
        tipo_informe = get_object_or_404(TipoInforme, id=tipo_id)
        tipo_informe.activo = not tipo_informe.activo
        tipo_informe.save()

        estado = 'activado' if tipo_informe.activo else 'desactivado'

        return JsonResponse({
            'success': True,
            'activo': tipo_informe.activo,
            'message': f'Tipo de informe "{tipo_informe.get_nombre_display()}" {estado} exitosamente.'
        })

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ... resto de las vistas existentes ...

@login_required
def documentos_recursos(request):
    """Vista para mostrar documentos y recursos de CONASEC"""
    # Filtros
    categoria_filtro = request.GET.get('categoria', '')
    buscar = request.GET.get('buscar', '')

    # Obtener recursos
    recursos = RecursoConasec.objects.filter(activo=True)

    if categoria_filtro:
        recursos = recursos.filter(categoria__icontains=categoria_filtro)

    if buscar:
        recursos = recursos.filter(
            Q(titulo__icontains=buscar) |
            Q(descripcion__icontains=buscar) |
            Q(categoria__icontains=buscar)
        )

    # Agrupar por categoría
    recursos_por_categoria = {}
    categorias = set()

    for recurso in recursos:
        categoria = recurso.categoria
        categorias.add(categoria)
        if categoria not in recursos_por_categoria:
            recursos_por_categoria[categoria] = []
        recursos_por_categoria[categoria].append(recurso)

    # Estadísticas
    total_recursos = RecursoConasec.objects.filter(activo=True).count()
    total_categorias = len(categorias)
    recursos_actualizados = RecursoConasec.objects.filter(
        fecha_actualizacion__date=date.today()
    ).count()

    context = {
        'recursos_por_categoria': recursos_por_categoria,
        'categorias': sorted(categorias),
        'total_recursos': total_recursos,
        'total_categorias': total_categorias,
        'recursos_actualizados': recursos_actualizados,
        'total_descargas': 0,  # Implementar contador si es necesario
    }

    return render(request, 'herramientas/documentos_recursos.html', context)


@login_required
def gestion_documentos(request):
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:dashboard')

    documentos = Documento.objects.all()

    # Filtros
    tipo_filtro = request.GET.get('tipo')
    buscar = request.GET.get('buscar')

    if tipo_filtro:
        documentos = documentos.filter(tipo=tipo_filtro)

    if buscar:
        documentos = documentos.filter(
            Q(titulo__icontains=buscar) |
            Q(descripcion__icontains=buscar)
        )

    # Ordenar por fecha de subida descendente
    documentos = documentos.order_by('-fecha_subida')

    # Paginación
    paginator = Paginator(documentos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'documentos': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }

    return render(request, 'herramientas/gestion_documentos.html', context)


@login_required
def subir_documento(request):
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para subir documentos.')
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.usuario_subida = request.user
            documento.save()
            messages.success(request, 'Documento subido exitosamente.')
            return redirect('herramientas:gestion_documentos')
    else:
        form = DocumentoForm()

    return render(request, 'herramientas/subir_documento.html', {'form': form})


@login_required
def organizar_carpetas(request):
    """Vista para organizar documentos por carpetas según estructura CORESEC"""
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para organizar carpetas.')
        return redirect('dashboard:dashboard')

    # Estructura de carpetas CORESEC
    estructura_carpetas = {
        'INFORMES': {
            'Huamalíes': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Huacaybamba': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Leoncio Prado': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Yarowilca': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Pachitea': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Marañón': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Ambo': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Lauricocha': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Huánuco': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Puerto Inca': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            'Dos de Mayo': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
        },
        'DOCUMENTOS_NORMATIVOS': ['Resoluciones', 'Directivas', 'Manuales', 'Protocolos'],
        'CAPACITACIONES': ['Materiales', 'Presentaciones', 'Videos', 'Evaluaciones'],
        'REPORTES_CORESEC': ['Mensuales', 'Trimestrales', 'Anuales', 'Especiales']
    }

    if request.method == 'POST':
        # Crear estructura de carpetas físicas
        crear_estructura_carpetas(estructura_carpetas)
        messages.success(request, 'Estructura de carpetas creada exitosamente.')
        return redirect('herramientas:gestion_documentos')

    context = {
        'estructura_carpetas': estructura_carpetas,
    }

    return render(request, 'herramientas/organizar_carpetas.html', context)


def crear_estructura_carpetas(estructura):
    """Crear estructura de carpetas en el sistema de archivos"""
    base_path = os.path.join(settings.MEDIA_ROOT, 'coresec_documentos')

    for carpeta_principal, subcarpetas in estructura.items():
        carpeta_path = os.path.join(base_path, carpeta_principal)
        os.makedirs(carpeta_path, exist_ok=True)

        if isinstance(subcarpetas, dict):
            # Para INFORMES (municipalidades)
            for municipalidad, categorias in subcarpetas.items():
                municipalidad_path = os.path.join(carpeta_path, municipalidad)
                os.makedirs(municipalidad_path, exist_ok=True)

                for categoria in categorias:
                    categoria_path = os.path.join(municipalidad_path, categoria)
                    os.makedirs(categoria_path, exist_ok=True)
        else:
            # Para otras carpetas
            for subcarpeta in subcarpetas:
                subcarpeta_path = os.path.join(carpeta_path, subcarpeta)
                os.makedirs(subcarpeta_path, exist_ok=True)


@login_required
def explorador_archivos(request):
    """Explorador de archivos estilo Windows para navegar por la estructura"""
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para acceder al explorador.')
        return redirect('dashboard:dashboard')

    ruta_actual = request.GET.get('path', '')
    base_path = os.path.join(settings.MEDIA_ROOT, 'coresec_documentos')

    if ruta_actual:
        ruta_completa = os.path.join(base_path, ruta_actual)
    else:
        ruta_completa = base_path

    # Verificar que la ruta existe y está dentro del directorio permitido
    if not os.path.exists(ruta_completa) or not ruta_completa.startswith(base_path):
        ruta_completa = base_path
        ruta_actual = ''

    carpetas = []
    archivos = []

    try:
        for item in os.listdir(ruta_completa):
            item_path = os.path.join(ruta_completa, item)
            if os.path.isdir(item_path):
                carpetas.append({
                    'nombre': item,
                    'ruta': os.path.join(ruta_actual, item).replace('\\', '/'),
                    'tipo': 'carpeta'
                })
            else:
                archivos.append({
                    'nombre': item,
                    'ruta': os.path.join(ruta_actual, item).replace('\\', '/'),
                    'tamaño': os.path.getsize(item_path),
                    'tipo': 'archivo'
                })
    except PermissionError:
        messages.error(request, 'No tienes permisos para acceder a esta carpeta.')
        return redirect('herramientas:explorador_archivos')

    # Ruta de navegación (breadcrumb)
    breadcrumb = []
    if ruta_actual:
        partes = ruta_actual.split('/')
        ruta_acumulada = ''
        for parte in partes:
            ruta_acumulada = os.path.join(ruta_acumulada, parte).replace('\\', '/')
            breadcrumb.append({
                'nombre': parte,
                'ruta': ruta_acumulada
            })

    context = {
        'ruta_actual': ruta_actual,
        'carpetas': sorted(carpetas, key=lambda x: x['nombre']),
        'archivos': sorted(archivos, key=lambda x: x['nombre']),
        'breadcrumb': breadcrumb,
        'puede_subir': True,  # Los admin/coordinadores pueden subir archivos
    }

    return render(request, 'herramientas/explorador_archivos.html', context)


@login_required
def gestion_informacion(request):
    """Vista principal para la gestión de información con explorador de archivos"""
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:dashboard')

    ruta_actual = request.GET.get('path', '')
    base_path = os.path.join(settings.MEDIA_ROOT, 'INFORMES')

    # Crear estructura base si no existe
    crear_estructura_informes()

    if ruta_actual:
        ruta_completa = os.path.join(base_path, ruta_actual)
    else:
        ruta_completa = base_path

    # Verificar que la ruta existe y está dentro del directorio permitido
    if not os.path.exists(ruta_completa) or not ruta_completa.startswith(base_path):
        ruta_completa = base_path
        ruta_actual = ''

    carpetas = []
    archivos = []

    try:
        for item in os.listdir(ruta_completa):
            item_path = os.path.join(ruta_completa, item)
            if os.path.isdir(item_path):
                carpetas.append({
                    'nombre': item,
                    'ruta': os.path.join(ruta_actual, item).replace('\\', '/'),
                    'tipo': 'carpeta'
                })
            else:
                archivos.append({
                    'nombre': item,
                    'ruta': os.path.join(ruta_actual, item).replace('\\', '/'),
                    'tamaño': os.path.getsize(item_path),
                    'tipo': 'archivo'
                })
    except PermissionError:
        messages.error(request, 'No tienes permisos para acceder a esta carpeta.')
        return redirect('herramientas:gestion_informacion')

    # Ruta de navegación (breadcrumb)
    breadcrumb = []
    if ruta_actual:
        partes = ruta_actual.split('/')
        ruta_acumulada = ''
        for parte in partes:
            ruta_acumulada = os.path.join(ruta_acumulada, parte).replace('\\', '/')
            breadcrumb.append({
                'nombre': parte,
                'ruta': ruta_acumulada
            })

    context = {
        'ruta_actual': ruta_actual,
        'carpetas': sorted(carpetas, key=lambda x: x['nombre']),
        'archivos': sorted(archivos, key=lambda x: x['nombre']),
        'breadcrumb': breadcrumb,
        'puede_subir': True,
    }

    return render(request, 'herramientas/gestion_informacion.html', context)


def crear_estructura_informes():
    """Crear estructura de carpetas para informes"""
    municipalidades = [
        'Huamalíes', 'Huacaybamba', 'Leoncio Prado', 'Yarowilca', 'Pachitea',
        'Marañón', 'Ambo', 'Lauricocha', 'Huánuco', 'Puerto Inca', 'Dos de Mayo'
    ]

    categorias = ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS']
    años = ['2024', '2025', '2026', '2027', '2028', '2029', '2030']
    periodos = ['PRIMER_TRIMESTRE', 'SEGUNDO_TRIMESTRE', 'TERCER_TRIMESTRE', 'CUARTO_TRIMESTRE', 'ANUAL']

    base_path = os.path.join(settings.MEDIA_ROOT, 'INFORMES')

    for municipalidad in municipalidades:
        municipalidad_path = os.path.join(base_path, municipalidad)
        os.makedirs(municipalidad_path, exist_ok=True)

        for categoria in categorias:
            categoria_path = os.path.join(municipalidad_path, categoria)
            os.makedirs(categoria_path, exist_ok=True)

            for año in años:
                año_path = os.path.join(categoria_path, año)
                os.makedirs(año_path, exist_ok=True)

                for periodo in periodos:
                    periodo_path = os.path.join(año_path, periodo)
                    os.makedirs(periodo_path, exist_ok=True)