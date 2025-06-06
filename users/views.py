from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import UserRegisterForm, UserUpdateForm, AdminUserUpdateForm, AdminPasswordChangeForm, UserLoginForm
from .models import User

class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Generar un username único basado en el email
            email = form.cleaned_data.get('email')
            username = email.split('@')[0]
            
            # Verificar si el username ya existe y añadir un número si es necesario
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            # Asignar el username único
            user = form.save(commit=False)
            user.username = username
            user.save()
            
            login(request, user)
            messages.success(request, 'Tu cuenta ha sido creada. Bienvenido al sistema ITCA360.')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})

def is_admin_or_coordinator(user):
    return user.role in ['ADMIN', 'COORDINATOR']

@login_required
@user_passes_test(is_admin_or_coordinator)
def user_list(request):
    if request.user.role == 'ADMIN':
        users = User.objects.all().order_by('-date_joined')
    else:  # Coordinador
        users = User.objects.filter(role='MUNICIPAL_MANAGER').order_by('-date_joined')
    
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.role == 'ADMIN')
def user_create(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Generar un username único basado en el email
            email = form.cleaned_data.get('email')
            username = email.split('@')[0]
            
            # Verificar si el username ya existe y añadir un número si es necesario
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            # Asignar el username único
            user = form.save(commit=False)
            user.username = username
            user.save()
            
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('user_list')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Crear Usuario'})

@login_required
@user_passes_test(lambda u: u.role == 'ADMIN')
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('user_list')
    else:
        form = AdminUserUpdateForm(instance=user)
    
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Editar Usuario', 'user_obj': user})

@login_required
@user_passes_test(lambda u: u.role == 'ADMIN')
def user_change_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminPasswordChangeForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, 'Contraseña actualizada exitosamente.')
            return redirect('user_list')
    else:
        form = AdminPasswordChangeForm()
    
    return render(request, 'users/password_change.html', {'form': form, 'user_obj': user})

@login_required
@user_passes_test(lambda u: u.role == 'ADMIN')
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "activado" if user.is_active else "desactivado"
    messages.success(request, f'Usuario {user.email} {status} exitosamente.')
    
    return redirect('user_list')
