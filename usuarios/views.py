from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import RegistroForm
from .models import Usuario


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.get_full_name() or user.username}')
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Credenciales inválidas')

    return render(request, 'usuarios/login.html')


@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('usuarios:login')


def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            tipo_usuario = form.cleaned_data['tipo_usuario']
            user.tipo_usuario = tipo_usuario

            if tipo_usuario == 'municipal':
                user.municipalidad = form.cleaned_data['municipalidad']
                user.cargo_municipal = form.cleaned_data['cargo_municipal']
            else:
                user.cargo_coresec = form.cleaned_data['cargo_coresec']

            user.telefono = form.cleaned_data.get('telefono', '')
            user.direccion = form.cleaned_data.get('direccion', '')

            user.save()

            messages.success(request, f'Usuario {user.get_full_name()} creado exitosamente.')
            return redirect('usuarios:login')
        else:
            messages.error(request, 'Error al crear el usuario. Verifica los datos.')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def perfil_view(request):
    context = {'user': request.user}

    try:
        from reportes.models import Informe

        if request.user.tipo_usuario == 'municipal':
            context.update({
                'mis_informes': Informe.objects.filter(usuario=request.user).count(),
                'mis_pendientes': Informe.objects.filter(usuario=request.user,
                                                         estado__in=['pendiente', 'en_revision']).count(),
                'mis_aprobados': Informe.objects.filter(usuario=request.user, estado='aprobado').count(),
            })
        else:
            context.update({
                'total_usuarios': Usuario.objects.count(),
                'total_informes': Informe.objects.count(),
                'informes_pendientes': Informe.objects.filter(estado='pendiente').count(),
            })
    except ImportError:
        pass

    return render(request, 'usuarios/perfil.html', context)


@login_required
def gestion_usuarios_view(request):
    if request.user.tipo_usuario != 'administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:dashboard')

    usuarios = Usuario.objects.all().order_by('-date_joined')

    context = {
        'usuarios': usuarios,
        'total_usuarios': usuarios.count(),
        'usuarios_activos': usuarios.filter(is_active=True).count(),
        'administradores': usuarios.filter(tipo_usuario='administrador').count(),
        'coordinadores': usuarios.filter(tipo_usuario='coordinador').count(),
        'municipales': usuarios.filter(tipo_usuario='municipal').count(),
    }

    return render(request, 'usuarios/gestion_usuarios.html', context)
