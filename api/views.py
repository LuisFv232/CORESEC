from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from reportes.models import Informe, TipoInforme
from usuarios.models import Usuario
from .serializers import InformeSerializer, EstadisticasSerializer

class InformeViewSet(viewsets.ModelViewSet):
    """API REST para informes"""
    serializer_class = InformeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.tipo_usuario in ['administrador', 'coordinador']:
            return Informe.objects.all()
        return Informe.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Endpoint para obtener estadísticas"""
        if request.user.tipo_usuario in ['administrador', 'coordinador']:
            # Estadísticas globales
            stats = {
                'total_informes': Informe.objects.count(),
                'por_estado': dict(Informe.objects.values_list('estado').annotate(Count('estado'))),
                'por_municipalidad': dict(
                    Informe.objects.values_list('usuario__municipalidad')
                    .annotate(Count('usuario__municipalidad'))
                ),
                'por_tipo': dict(
                    Informe.objects.values_list('tipo__nombre')
                    .annotate(Count('tipo__nombre'))
                )
            }
        else:
            # Estadísticas del usuario
            stats = {
                'mis_informes': Informe.objects.filter(usuario=request.user).count(),
                'por_estado': dict(
                    Informe.objects.filter(usuario=request.user)
                    .values_list('estado').annotate(Count('estado'))
                ),
                'por_tipo': dict(
                    Informe.objects.filter(usuario=request.user)
                    .values_list('tipo__nombre').annotate(Count('tipo__nombre'))
                )
            }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de un informe"""
        if request.user.tipo_usuario not in ['administrador', 'coordinador']:
            return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        informe = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado in ['pendiente', 'en_revision', 'observado', 'atendido', 'aprobado']:
            informe.estado = nuevo_estado
            informe.save()
            
            # Enviar notificación
            from utils.email_notifications import enviar_notificacion_cambio_estado
            enviar_notificacion_cambio_estado(informe, nuevo_estado, request.user)
            
            return Response({'mensaje': 'Estado actualizado', 'nuevo_estado': nuevo_estado})
        
        return Response({'error': 'Estado inválido'}, status=status.HTTP_400_BAD_REQUEST)
