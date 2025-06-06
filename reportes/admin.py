from django.contrib import admin
from .models import TipoInforme, Informe, RespuestaInforme, TipoDocumentoRespuesta
from .forms import TipoInformeForm, TipoDocumentoRespuestaForm


class TipoInformeAdmin(admin.ModelAdmin):
    form = TipoInformeForm
    list_display = ('nombre_display', 'activo', 'permite_municipal', 'permite_admin', 'permite_coordinador')
    list_filter = ('activo', 'permite_municipal', 'permite_admin', 'permite_coordinador')
    search_fields = ('nombre', 'nombre_display')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'nombre_display', 'descripcion', 'activo')
        }),
        ('Configuración de Campos', {
            'fields': ('requiere_trimestre', 'requiere_fecha', 'requiere_informe_padre', 'permite_adjuntos')
        }),
        ('Estructura de Carpetas', {
            'fields': ('estructura_carpetas',)
        }),
        ('Permisos por Tipo de Usuario', {
            'fields': ('permite_municipal', 'permite_admin', 'permite_coordinador')
        })
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Crear estructura de carpetas para todas las municipalidades
        from usuarios.models import Usuario
        for codigo, nombre in Usuario.MUNICIPALIDADES_HUANUCO:
            obj.crear_estructura(codigo)


class TipoDocumentoRespuestaAdmin(admin.ModelAdmin):
    form = TipoDocumentoRespuestaForm
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


class InformeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'usuario', 'estado', 'fecha_subida')
    list_filter = ('tipo', 'estado', 'usuario__municipalidad')
    search_fields = ('titulo', 'descripcion')
    raw_id_fields = ('usuario', 'informe_padre')
    date_hierarchy = 'fecha_subida'


class RespuestaInformeAdmin(admin.ModelAdmin):
    list_display = ('informe', 'usuario', 'tipo_documento', 'fecha_respuesta')
    list_filter = ('tipo_documento', 'usuario')
    search_fields = ('mensaje',)
    raw_id_fields = ('informe', 'usuario')


admin.site.register(TipoInforme, TipoInformeAdmin)
admin.site.register(Informe, InformeAdmin)
admin.site.register(RespuestaInforme, RespuestaInformeAdmin)
admin.site.register(TipoDocumentoRespuesta, TipoDocumentoRespuestaAdmin)