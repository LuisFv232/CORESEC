import os
from django.core.management.base import BaseCommand
from django.conf import settings
from usuarios.models import Usuario
from reportes.models import TipoInforme
from notificaciones.models import Notificacion

class Command(BaseCommand):
    help = 'Configuración inicial completa de CORESEC'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Iniciando configuración de CORESEC...")
        
        # 1. Crear estructura de carpetas
        self.crear_estructura_carpetas()
        
        # 2. Crear tipos de informe
        self.crear_tipos_informe()
        
        # 3. Crear usuario administrador por defecto
        self.crear_admin_default()
        
        # 4. Crear notificaciones de bienvenida
        self.crear_notificaciones_bienvenida()
        
        self.stdout.write("✅ ¡CORESEC configurado exitosamente!")

    def crear_estructura_carpetas(self):
        """Crear estructura de carpetas del sistema"""
        base_path = os.path.join(settings.MEDIA_ROOT, 'coresec_documentos')
        
        estructura = {
            'INFORMES': {
                'Huamalies': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Huacaybamba': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Leoncio_Prado': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Yarowilca': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Pachitea': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Maranon': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Ambo': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Lauricocha': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Huanuco': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Puerto_Inca': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
                'Dos_de_Mayo': ['ITCA', 'FICHA_VERIFICACION', 'SUPERVISIONES', 'ITS', 'IAS'],
            },
            'DOCUMENTOS_NORMATIVOS': ['Resoluciones', 'Directivas', 'Manuales', 'Protocolos'],
            'CAPACITACIONES': ['Materiales', 'Presentaciones', 'Videos', 'Evaluaciones'],
            'REPORTES_CORESEC': ['Mensuales', 'Trimestrales', 'Anuales', 'Especiales']
        }
        
        for carpeta_principal, subcarpetas in estructura.items():
            carpeta_path = os.path.join(base_path, carpeta_principal)
            os.makedirs(carpeta_path, exist_ok=True)
            
            if isinstance(subcarpetas, dict):
                for municipalidad, categorias in subcarpetas.items():
                    municipalidad_path = os.path.join(carpeta_path, municipalidad)
                    os.makedirs(municipalidad_path, exist_ok=True)
                    
                    for categoria in categorias:
                        categoria_path = os.path.join(municipalidad_path, categoria)
                        os.makedirs(categoria_path, exist_ok=True)
            else:
                for subcarpeta in subcarpetas:
                    subcarpeta_path = os.path.join(carpeta_path, subcarpeta)
                    os.makedirs(subcarpeta_path, exist_ok=True)
        
        self.stdout.write("📁 Estructura de carpetas creada")

    def crear_tipos_informe(self):
        """Crear tipos de informe predefinidos"""
        tipos = [
            ('itca_trimestral', 'Informe Trimestral de Actividades ITCA', 'itca', True),
            ('anual_seguimiento', 'Informe Anual de Seguimiento', 'itca', False),
            ('anual_evaluacion', 'Informe Anual de Evaluación', 'itca', False),
            ('ficha_verificacion', 'Ficha de Verificación', 'ficha_verificacion', True),
            ('supervision', 'Informe de Supervisión', 'supervisiones', False),
            ('its', 'Informe ITS', 'its', True),
            ('ias', 'Informe IAS', 'ias', True),
        ]
        
        for nombre, descripcion, categoria, requiere_periodo in tipos:
            TipoInforme.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': descripcion,
                    'categoria': categoria,
                    'requiere_periodo': requiere_periodo,
                    'activo': True
                }
            )
        
        self.stdout.write("📋 Tipos de informe creados")

    def crear_admin_default(self):
        """Crear usuario administrador por defecto"""
        if not Usuario.objects.filter(username='admin_coresec').exists():
            admin = Usuario.objects.create_user(
                username='admin_coresec',
                email='admin@coresec.gob.pe',
                password='Coresec2024!',
                first_name='Administrador',
                last_name='CORESEC',
                tipo_usuario='administrador',
                cargo_coresec='director_ejecutivo',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write("👤 Usuario administrador creado: admin_coresec / Coresec2024!")

    def crear_notificaciones_bienvenida(self):
        """Crear notificaciones de bienvenida para todos los usuarios"""
        usuarios = Usuario.objects.all()
        
        for usuario in usuarios:
            if not Notificacion.objects.filter(usuario=usuario, titulo__contains='Bienvenido').exists():
                Notificacion.objects.create(
                    usuario=usuario,
                    titulo=f'Bienvenido al Sistema CORESEC',
                    mensaje=f'Hola {usuario.first_name}, bienvenido al Sistema de Gestión de Informes de CORESEC Huánuco. Aquí podrás gestionar todos tus informes de manera eficiente.',
                    tipo='info'
                )
        
        self.stdout.write("🔔 Notificaciones de bienvenida creadas")
