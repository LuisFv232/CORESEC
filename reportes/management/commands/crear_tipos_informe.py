from django.core.management.base import BaseCommand
from reportes.models import TipoInforme

class Command(BaseCommand):
    help = 'Crea los tipos de informe básicos del sistema'

    def handle(self, *args, **options):
        tipos_informe = [
            {
                'nombre': 'itca',
                'descripcion': 'Informe Técnico de Cumplimiento Ambiental',
                'requiere_periodo': True,
                'permite_municipal': True,
                'permite_admin': False,
                'permite_coordinador': False,
                'activo': True,
            },
            {
                'nombre': 'ias',
                'descripcion': 'Informe Anual de Sostenibilidad',
                'requiere_periodo': False,
                'permite_municipal': True,
                'permite_admin': True,
                'permite_coordinador': True,
                'activo': True,
            },
            {
                'nombre': 'ficha_verificacion',
                'descripcion': 'Ficha de Verificación',
                'requiere_periodo': True,
                'permite_municipal': False,
                'permite_admin': True,
                'permite_coordinador': True,
                'activo': True,
            },
            {
                'nombre': 'supervisiones',
                'descripcion': 'Supervisiones',
                'requiere_periodo': True,
                'permite_municipal': False,
                'permite_admin': True,
                'permite_coordinador': True,
                'activo': True,
            },
            {
                'nombre': 'its',
                'descripcion': 'Informe Técnico de Supervisión',
                'requiere_periodo': False,
                'permite_municipal': False,
                'permite_admin': True,
                'permite_coordinador': True,
                'activo': True,
            },
        ]

        for tipo_data in tipos_informe:
            tipo, created = TipoInforme.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults=tipo_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Tipo de informe "{tipo.get_nombre_display()}" creado exitosamente')
                )
            else:
                # Actualizar permisos si ya existe
                for key, value in tipo_data.items():
                    if key != 'nombre':
                        setattr(tipo, key, value)
                tipo.save()
                self.stdout.write(
                    self.style.WARNING(f'🔄 Tipo de informe "{tipo.get_nombre_display()}" actualizado')
                )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Proceso completado. Todos los tipos de informe están disponibles.')
        )
        
        # Mostrar resumen
        self.stdout.write('\n📋 RESUMEN DE PERMISOS:')
        for tipo in TipoInforme.objects.filter(activo=True):
            permisos = []
            if tipo.permite_municipal:
                permisos.append('Municipal')
            if tipo.permite_admin:
                permisos.append('Administrador')
            if tipo.permite_coordinador:
                permisos.append('Coordinador')
            
            self.stdout.write(f'   • {tipo.get_nombre_display()}: {", ".join(permisos)}')
