import os
import shutil
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Crear backup completo del sistema CORESEC'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'coresec_backup_{timestamp}'
        backup_path = os.path.join(settings.BASE_DIR, 'backups', backup_name)
        
        os.makedirs(backup_path, exist_ok=True)
        
        # 1. Backup de la base de datos
        self.backup_database(backup_path)
        
        # 2. Backup de archivos media
        self.backup_media_files(backup_path)
        
        # 3. Backup de configuración
        self.backup_config_files(backup_path)
        
        # 4. Crear ZIP
        zip_path = f'{backup_path}.zip'
        self.create_zip(backup_path, zip_path)
        
        # 5. Limpiar carpeta temporal
        shutil.rmtree(backup_path)
        
        self.stdout.write(f"✅ Backup creado: {zip_path}")

    def backup_database(self, backup_path):
        """Backup de la base de datos SQLite"""
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            shutil.copy2(db_path, os.path.join(backup_path, 'database.sqlite3'))
            self.stdout.write("📊 Base de datos respaldada")

    def backup_media_files(self, backup_path):
        """Backup de archivos media"""
        media_backup_path = os.path.join(backup_path, 'media')
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.copytree(settings.MEDIA_ROOT, media_backup_path)
            self.stdout.write("📁 Archivos media respaldados")

    def backup_config_files(self, backup_path):
        """Backup de archivos de configuración importantes"""
        config_files = ['settings.py', 'urls.py', 'requirements.txt']
        config_backup_path = os.path.join(backup_path, 'config')
        os.makedirs(config_backup_path, exist_ok=True)
        
        for config_file in config_files:
            file_path = os.path.join(settings.BASE_DIR, config_file)
            if os.path.exists(file_path):
                shutil.copy2(file_path, config_backup_path)
        
        self.stdout.write("⚙️ Configuración respaldada")

    def create_zip(self, source_path, zip_path):
        """Crear archivo ZIP del backup"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_path)
                    zipf.write(file_path, arcname)
