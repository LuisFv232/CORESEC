from django.core.management.base import BaseCommand
from herramientas.models import CarpetaMunicipal

class Command(BaseCommand):
    help = 'Limpia carpetas vacías sin documentos'

    def handle(self, *args, **options):
        carpetas_vacias = CarpetaMunicipal.objects.filter(documentos__isnull=True)
        count = carpetas_vacias.count()
        
        if count > 0:
            carpetas_vacias.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Se eliminaron {count} carpetas vacías')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No se encontraron carpetas vacías')
            )
