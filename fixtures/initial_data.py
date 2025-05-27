# Script para crear datos iniciales
from django.core.management.base import BaseCommand
from reportes.models import TipoInforme
from notificaciones.models import Notificacion
from usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Crea datos iniciales para CORESEC'

    def handle(self, *args, **options):
        # Crear tipos de informe
        tipos_informe = [
            {
                'nombre': 'itca_trimestral',
                'descripcion': 'Informe Trimestral de Actividades ITCA',
                'categoria': 'itca',
                'requiere_periodo': True
            },
            {
                'nombre': 'anual_seguimiento',
                'descripcion': 'Informe Anual de Seguimiento',
                'categoria': 'itca',
                'requiere_periodo': False
            },
            {
                'nombre': 'ficha_verificacion',
                'descripcion': 'Ficha de Verificación',
                'categoria': 'ficha_verificacion',
                'requiere_periodo': True
            },
            {
                'nombre': 'supervision',
                'descripcion': 'Informe de Supervisión',
                'categoria': 'supervisiones',
                'requiere_periodo': False
            },
            {
                'nombre': 'its',
                'descripcion': 'Informe ITS',
                'categoria': 'its',
                'requiere_periodo': True
            },
            {
                'nombre': 'ias',
                'descripcion': 'Informe IAS',
                'categoria': 'ias',
                'requiere_periodo': True
            }
        ]
        
        for tipo_data in tipos_informe:
            tipo, created = TipoInforme.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f"✅ Creado tipo: {tipo.get_nombre_display()}")
        
        self.stdout.write("🎉 Datos iniciales creados exitosamente!")
