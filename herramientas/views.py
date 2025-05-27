from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Documento, Enlace, RecursoConasec
from .forms import DocumentoForm, EnlaceForm
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
    
    context = {
        'documentos_recientes': documentos_recientes,
        'enlaces_institucionales': enlaces_institucionales,
        'enlaces_academicos': enlaces_academicos,
        'enlaces_soporte': enlaces_soporte,
    }
    
    return render(request, 'herramientas/herramientas.html', context)

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
