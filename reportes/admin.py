from django.contrib import admin
from .models import TipoInforme, Informe, RespuestaInforme


@admin.register(TipoInforme)
class TipoInformeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'requiere_periodo', 'activo', 'fecha_creacion']
    list_filter = ['requiere_periodo', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']


@admin.register(Informe)
class InformeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'tipo', 'estado', 'año', 'trimestre', 'fecha_subida']
    list_filter = ['estado', 'tipo', 'año', 'trimestre', 'fecha_subida', 'usuario__municipalidad']
    search_fields = ['titulo', 'descripcion', 'usuario__username', 'usuario__first_name', 'usuario__last_name']
    list_editable = ['estado']
    readonly_fields = ['fecha_subida', 'fecha_actualizacion']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.tipo_usuario == 'municipal':
            return qs.filter(usuario=request.user)
        return qs


@admin.register(RespuestaInforme)
class RespuestaInformeAdmin(admin.ModelAdmin):
    list_display = ['informe', 'usuario', 'fecha_respuesta']
    list_filter = ['fecha_respuesta', 'usuario__tipo_usuario']
    search_fields = ['informe__titulo', 'usuario__username', 'mensaje']
    readonly_fields = ['fecha_respuesta']
