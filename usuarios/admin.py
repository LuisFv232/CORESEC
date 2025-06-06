from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'municipalidad', 'activo', 'date_joined']
    list_filter = ['tipo_usuario', 'municipalidad', 'activo', 'cargo_coresec', 'cargo_municipal', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_editable = ['activo']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información CORESEC', {
            'fields': ('telefono', 'direccion', 'tipo_usuario', 'municipalidad', 'cargo_coresec', 'cargo_municipal', 'activo')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información CORESEC', {
            'fields': ('telefono', 'direccion', 'tipo_usuario', 'municipalidad', 'cargo_coresec', 'cargo_municipal')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.tipo_usuario == 'municipal':
            return qs.filter(id=request.user.id)
        return qs
