#!/bin/bash

echo "🚀 Desplegando CORESEC..."

# 1. Actualizar código
git pull origin main

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# 5. Recopilar archivos estáticos
python manage.py collectstatic --noinput

# 6. Configurar CORESEC
python manage.py setup_coresec

# 7. Crear backup antes del despliegue
python manage.py backup_system

# 8. Reiniciar servicios (si usa systemd)
# sudo systemctl restart coresec
# sudo systemctl restart nginx

echo "✅ Despliegue completado!"
