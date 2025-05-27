from django.core.management.base import BaseCommand
from herramientas.models import CategoriaDocumento, Documento
from django.contrib.auth import get_user_model
from herramientas.models import DocumentoMunicipal
from usuarios.models import Usuario
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Carga documentos y categorías iniciales'

    def handle(self, *args, **options):
        # Crear categorías por defecto
        categorias = [
            ('Manuales', 'Manuales de procedimientos y guías'),
            ('Formularios', 'Formularios oficiales'),
            ('Normativas', 'Leyes, reglamentos y normativas'),
            ('Informes', 'Informes y reportes oficiales'),
        ]
        
        for nombre, descripcion in categorias:
            categoria, created = CategoriaDocumento.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Categoría creada: {nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Categorías iniciales cargadas exitosamente')
        )

        # Crear categorías iniciales
        categorias_data = [
            {
                'nombre': 'Formularios Oficiales',
                'descripcion': 'Formularios y documentos oficiales para trámites municipales',
                'icono': 'fas fa-file-alt',
                'color': '#25B87D',
                'orden': 1
            },
            {
                'nombre': 'Guías y Manuales',
                'descripcion': 'Guías paso a paso y manuales de procedimientos',
                'icono': 'fas fa-book',
                'color': '#3498db',
                'orden': 2
            },
            {
                'nombre': 'Plantillas',
                'descripcion': 'Plantillas editables para documentos comunes',
                'icono': 'fas fa-file-word',
                'color': '#e74c3c',
                'orden': 3
            },
            {
                'nombre': 'Recursos Técnicos',
                'descripcion': 'Documentos técnicos y especializados',
                'icono': 'fas fa-cogs',
                'color': '#f39c12',
                'orden': 4
            },
            {
                'nombre': 'Capacitación',
                'descripcion': 'Material de capacitación y entrenamiento',
                'icono': 'fas fa-graduation-cap',
                'color': '#9b59b6',
                'orden': 5
            },
            {
                'nombre': 'Normativas',
                'descripcion': 'Leyes, decretos y normativas aplicables',
                'icono': 'fas fa-gavel',
                'color': '#34495e',
                'orden': 6
            }
        ]

        for cat_data in categorias_data:
            categoria, created = CategoriaDocumento.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Categoría creada: {categoria.nombre}')
                )

        # Crear algunos documentos de ejemplo
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            
            if not admin_user:
                self.stdout.write(
                    self.style.WARNING('No se encontró un usuario administrador. Algunos documentos no tendrán autor asignado.')
                )
            
            documentos_ejemplo = [
                {
                    'titulo': 'Formulario de Solicitud de Licencia de Construcción',
                    'descripcion': 'Formulario oficial para solicitar licencias de construcción en el municipio.',
                    'categoria': CategoriaDocumento.objects.get(nombre='Formularios Oficiales'),
                    'destacado': True,
                    'palabras_clave': 'licencia, construcción, formulario, solicitud',
                    'autor': admin_user
                },
                {
                    'titulo': 'Guía para Trámites Municipales',
                    'descripcion': 'Guía completa con todos los trámites disponibles y sus requisitos.',
                    'categoria': CategoriaDocumento.objects.get(nombre='Guías y Manuales'),
                    'destacado': True,
                    'palabras_clave': 'trámites, guía, municipales, requisitos',
                    'autor': admin_user
                },
                {
                    'titulo': 'Plantilla de Informe Mensual',
                    'descripcion': 'Plantilla estándar para la elaboración de informes mensuales.',
                    'categoria': CategoriaDocumento.objects.get(nombre='Plantillas'),
                    'destacado': False,
                    'palabras_clave': 'plantilla, informe, mensual, formato',
                    'autor': admin_user
                },
                {
                    'titulo': 'Manual de Procedimientos Administrativos',
                    'descripcion': 'Manual detallado de todos los procedimientos administrativos del municipio.',
                    'categoria': CategoriaDocumento.objects.get(nombre='Guías y Manuales'),
                    'destacado': True,
                    'palabras_clave': 'manual, procedimientos, administrativos, municipio',
                    'autor': admin_user
                },
                {
                    'titulo': 'Especificaciones Técnicas para Obras Públicas',
                    'descripcion': 'Documento técnico con especificaciones para obras públicas municipales.',
                    'categoria': CategoriaDocumento.objects.get(nombre='Recursos Técnicos'),
                    'destacado': False,
                    'palabras_clave': 'especificaciones, técnicas, obras públicas',
                    'autor': admin_user
                },
                {
                    'titulo': 'Curso de Capacitación en Atención al Ciudadano',
                    'descripcion': 'Material de capacitación para mejorar la atención al ciudadano.',
                    'categoria': CategoriaDocumento.objects.get(nombre='Capacitación'),
                    'destacado': False,
                    'palabras_clave': 'capacitación, atención, ciudadano, servicio',
                    'autor': admin_user
                }
            ]

            for doc_data in documentos_ejemplo:
                documento, created = Documento.objects.get_or_create(
                    titulo=doc_data['titulo'],
                    defaults=doc_data
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Documento creado: {documento.titulo}')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear documentos de ejemplo: {str(e)}')
            )

        # Buscar algunas carpetas municipales para agregar documentos de ejemplo
        municipios_ejemplo = ['San Salvador', 'Santa Ana', 'San Miguel']
        
        for municipio_nombre in municipios_ejemplo:
            try:
                municipio = DocumentoMunicipal.objects.get(
                    nombre=municipio_nombre,
                    es_carpeta=True,
                    carpeta_padre=None
                )
                
                # Crear subcarpetas
                subcarpetas = ['Reportes 2024', 'Documentos Oficiales', 'Presupuestos']
                
                for subcarpeta_nombre in subcarpetas:
                    subcarpeta, created = DocumentoMunicipal.objects.get_or_create(
                        nombre=subcarpeta_nombre,
                        carpeta_padre=municipio,
                        es_carpeta=True,
                        defaults={
                            'ruta_completa': f'{municipio.ruta_completa}/{subcarpeta_nombre}'
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'✓ Creada subcarpeta: {subcarpeta.ruta_completa}')
                
            except DocumentoMunicipal.DoesNotExist:
                self.stdout.write(f'✗ No se encontró el municipio: {municipio_nombre}')
        
        # Verificar que existan usuarios
        usuarios = Usuario.objects.filter(activo=True)
        if not usuarios.exists():
            self.stdout.write(
                self.style.ERROR('No hay usuarios activos. Crea usuarios primero.')
            )
            return
        
        municipios = ['Santa Ana', 'Sonsonate', 'Ahuachapán', 'Metapán', 'Chalchuapa']
        tipos = ['acta', 'ordenanza', 'resolucion', 'informe', 'presupuesto']
        
        documentos_ejemplo = [
            'Acta de Sesión Ordinaria',
            'Ordenanza de Construcción',
            'Resolución de Presupuesto',
            'Informe de Gestión Municipal',
            'Presupuesto Anual',
            'Acta de Cabildo Abierto',
            'Ordenanza de Tránsito',
            'Resolución de Contratación'
        ]
        
        for i, nombre in enumerate(documentos_ejemplo):
            municipio = random.choice(municipios)
            tipo = random.choice(tipos)
            usuario = random.choice(usuarios)
            
            documento, created = DocumentoMunicipal.objects.get_or_create(
                nombre=nombre,
                municipio=municipio,
                defaults={
                    'descripcion': f'Documento de ejemplo para {municipio}',
                    'tipo': tipo,
                    'archivo': f'documentos_municipales/ejemplo_{i+1}.pdf',
                    'usuario_subida': usuario,
                    'fecha_documento': timezone.now().date(),
                }
            )
            
            if created:
                self.stdout.write(f'✓ Creado: {nombre} - {municipio}')
            else:
                self.stdout.write(f'- Ya existe: {nombre} - {municipio}')
        
        self.stdout.write(
            self.style.SUCCESS('Documentos de ejemplo cargados exitosamente.')
        )

        self.stdout.write(
            self.style.SUCCESS('Carga de datos iniciales completada exitosamente')
        )
