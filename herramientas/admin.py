from django.contrib import admin
from .models import Documento, Enlace

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
