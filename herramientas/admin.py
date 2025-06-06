from django.contrib import admin
from .models import Documento, Enlace, TipoDocumento
from .forms import TipoDocumentoForm

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'usuario_subida', 'fecha_subida', 'activo']
    list_filter = ['tipo', 'activo', 'fecha_subida']
    search_fields = ['titulo', 'descripcion']
    list_editable = ['activo']

@admin.register(Enlace)
class EnlaceAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'usuario', 'fecha_creacion', 'activo']  # Asumiendo que el campo correcto es 'usuario'
    list_filter = ['categoria', 'activo', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion', 'url']
    list_editable = ['activo']
class TipoDocumentoAdmin(admin.ModelAdmin):
    form = TipoDocumentoForm
    list_display = ('nombre', 'prefijo_carpeta', 'activo', 'permite_municipal', 'permite_admin', 'permite_coordinador')
    list_filter = ('activo', 'permite_municipal', 'permite_admin', 'permite_coordinador')
    search_fields = ('nombre', 'descripcion')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'prefijo_carpeta', 'activo')
        }),
        ('Permisos por Tipo de Usuario', {
            'fields': ('permite_municipal', 'permite_admin', 'permite_coordinador')
        })
    )

admin.site.register(TipoDocumento, TipoDocumentoAdmin)