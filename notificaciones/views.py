from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone


@login_required
def notificaciones_view(request):
    """Vista principal de notificaciones"""
    # Simulamos notificaciones por ahora
    notificaciones = []  # Aquí irían las notificaciones reales

    context = {
        'notificaciones': notificaciones,
        'no_leidas': len([n for n in notificaciones if not n['leida']]),
        'total': len(notificaciones)
    }

    return render(request, 'notificaciones/notificaciones.html', context)


@login_required
def marcar_leida(request, notificacion_id):
    """Marcar notificación como leída"""
    if request.method == 'POST':
        # Aquí marcarías la notificación como leída en la base de datos
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def crear_notificacion(request):
    """Crear nueva notificación - solo administradores"""
    if request.user.tipo_usuario not in ['administrador', 'coordinador']:
        messages.error(request, 'No tienes permisos para crear notificaciones.')
        return redirect('notificaciones:notificaciones')

    if request.method == 'POST':
        # Aquí procesarías la creación de la notificación
        messages.success(request, 'Notificación creada exitosamente.')
        return redirect('notificaciones:notificaciones')

    return render(request, 'notificaciones/crear_notificacion.html')
