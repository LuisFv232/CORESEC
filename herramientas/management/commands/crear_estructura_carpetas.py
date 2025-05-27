from django.core.management.base import BaseCommand
from herramientas.models import CarpetaMunicipal

class Command(BaseCommand):
    help = 'Crea la estructura básica de carpetas municipales'

    def add_arguments(self, parser):
        parser.add_argument('--municipio', type=str, help='Nombre del municipio')
        parser.add_argument('--año', type=int, help='Año para crear las carpetas')

    def handle(self, *args, **options):
        municipio = options.get('municipio', 'Ejemplo')
        año = options.get('año', 2024)
        
        # Estructura básica de carpetas
        estructura = [
            'INFORMES MENSUALES',
            'ACTAS',
            'ORDENANZAS',
            'RESOLUCIONES',
            'PRESUPUESTO',
            'PROYECTOS',
        ]
        
        for carpeta_nombre in estructura:
            ruta_completa = f"INFORMES/{municipio}/{carpeta_nombre}"
            
            carpeta, created = CarpetaMunicipal.objects.get_or_create(
                nombre=carpeta_nombre,
                municipio=municipio,
                año=año,
                ruta_completa=ruta_completa
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Carpeta creada: {ruta_completa}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Carpeta ya existe: {ruta_completa}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Estructura de carpetas creada para {municipio} - {año}')
        )
