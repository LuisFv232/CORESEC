
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import os
from datetime import datetime

User = get_user_model()

def upload_to_structured_path(instance, filename):
    """Genera la ruta estructurada para guardar archivos"""
    municipalidad = instance.usuario.get_municipalidad_display()
    tipo_informe = instance.tipo.nombre.upper()
    año = str(instance.año)
    
    # Crear la ruta base
    path_parts = ['INFORMES', municipalidad, tipo_informe, año]
    
    # Agregar período según el tipo
    if instance.tipo.nombre == 'itca' and instance.trimestre:
        trimestre_map = {
            1: 'PRIMER_TRIMESTRE',
            2: 'SEGUNDO_TRIMESTRE', 
            3: 'TERCER_TRIMESTRE',
            4: 'CUARTO_TRIMESTRE'
        }
        path_parts.append(trimestre_map.get(instance.trimestre, 'PRIMER_TRIMESTRE'))
    elif instance.tipo.nombre in ['ficha_verificacion', 'supervisiones'] and instance.fecha_informe:
        path_parts.append(instance.fecha_informe.strftime('%m-%B'))
    elif instance.tipo.nombre == 'ias':
        path_parts.append('ANUAL')
    elif instance.tipo.nombre == 'its' and instance.informe_padre:
        if instance.informe_padre.trimestre:
            trimestre_map = {
                1: 'PRIMER_TRIMESTRE',
                2: 'SEGUNDO_TRIMESTRE',
                3: 'TERCER_TRIMESTRE', 
                4: 'CUARTO_TRIMESTRE'
            }
            path_parts.append(trimestre_map.get(instance.informe_padre.trimestre, 'PRIMER_TRIMESTRE'))
    
    # Unir la ruta y agregar el nombre del archivo
    return os.path.join(*path_parts, filename)

class TipoInforme(models.Model):
    TIPOS_CHOICES = [
        ('itca', 'ITCA'),
        ('ficha_verificacion', 'Ficha de Verificación'),
        ('supervisiones', 'Supervisiones'),
        ('its', 'ITS'),
        ('ias', 'IAS'),
    ]
    
    nombre = models.CharField(max_length=50, choices=TIPOS_CHOICES, unique=True)
    descripcion = models.TextField()
    requiere_periodo = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Permisos por tipo de usuario
    permite_municipal = models.BooleanField(default=False)
    permite_admin = models.BooleanField(default=True)
    permite_coordinador = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tipo de Informe"
        verbose_name_plural = "Tipos de Informe"
    
    def __str__(self):
        return self.get_nombre_display()
    
    def puede_acceder(self, tipo_usuario):
        """Verifica si un tipo de usuario puede acceder a este tipo de informe"""
        if tipo_usuario == 'municipal':
            return self.permite_municipal
        elif tipo_usuario == 'administrador':
            return self.permite_admin
        elif tipo_usuario == 'coordinador':
            return self.permite_coordinador
        return False

class Informe(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('requiere_correccion', 'Requiere Corrección'),
    ]
    
    TRIMESTRE_CHOICES = [
        (1, 'Primer Trimestre'),
        (2, 'Segundo Trimestre'),
        (3, 'Tercer Trimestre'),
        (4, 'Cuarto Trimestre'),
    ]
    
    AÑO_CHOICES = [(year, str(year)) for year in range(2020, 2031)]
    
    # Campos básicos
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='informes')
    tipo = models.ForeignKey(TipoInforme, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    # Campos de tiempo
    año = models.IntegerField(choices=AÑO_CHOICES)
    trimestre = models.IntegerField(choices=TRIMESTRE_CHOICES, null=True, blank=True)
    fecha_informe = models.DateField(null=True, blank=True, help_text="Para Fichas de Verificación y Supervisiones")
    
    # Relación padre (para ITS que responden a ITCA)
    informe_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas_its')
    
    # Archivo y estado
    archivo_adjunto = models.FileField(
        upload_to=upload_to_structured_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx'])]
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Metadatos
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Informe"
        verbose_name_plural = "Informes"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.tipo} - {self.titulo} ({self.usuario.get_municipalidad_display()})"
    
    def get_periodo_display(self):
        """Retorna el período formateado según el tipo de informe"""
        if self.tipo.nombre == 'itca' and self.trimestre:
            return f"{self.get_trimestre_display()} {self.año}"
        elif self.tipo.nombre in ['ficha_verificacion', 'supervisiones'] and self.fecha_informe:
            return self.fecha_informe.strftime('%d/%m/%Y')
        elif self.tipo.nombre == 'ias':
            return f"Año {self.año}"
        return f"Año {self.año}"


class TipoDocumentoRespuesta(models.Model):
    TIPOS_RESPUESTA_CHOICES = [
        ('oficio', 'Oficio'),
        ('memorando', 'Memorando'),
        ('carta', 'Carta'),
        ('informe_tecnico', 'Informe Técnico'),
        ('acta', 'Acta'),
        ('resolucion', 'Resolución'),
        ('dictamen', 'Dictamen'),
        ('notificacion', 'Notificación'),
        ('otro', 'Otro Documento'),
    ]

    nombre = models.CharField(max_length=50, choices=TIPOS_RESPUESTA_CHOICES, unique=True)
    descripcion = models.TextField()
    prefijo_carpeta = models.CharField(max_length=20, help_text="Prefijo para la carpeta (ej: OFICIOS, MEMORANDOS)")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tipo de Documento de Respuesta"
        verbose_name_plural = "Tipos de Documentos de Respuesta"

    def __str__(self):
        return self.get_nombre_display()


# FUNCIÓN MEJORADA para upload de respuestas
def upload_respuesta_to_structured_path(instance, filename):
    """Genera la ruta estructurada para guardar respuestas de informes"""
    informe = instance.informe
    tipo_documento = instance.tipo_documento

    # Validar que exista el informe y tipo de documento
    if not informe or not tipo_documento:
        raise ValueError("Falta información requerida para generar la ruta de almacenamiento")

    # Usar la municipalidad del INFORME ORIGINAL
    municipalidad = informe.usuario.get_municipalidad_display()
    tipo_informe = informe.tipo.nombre.upper()
    año = str(informe.año)

    # Crear la ruta base igual que el informe original
    path_parts = ['INFORMES', municipalidad, tipo_informe, año]

    # Agregar período según el tipo del informe original
    if informe.tipo.nombre == 'itca' and informe.trimestre:
        trimestre_map = {
            1: 'PRIMER_TRIMESTRE',
            2: 'SEGUNDO_TRIMESTRE',
            3: 'TERCER_TRIMESTRE',
            4: 'CUARTO_TRIMESTRE'
        }
        path_parts.append(trimestre_map.get(informe.trimestre, 'PRIMER_TRIMESTRE'))
    elif informe.tipo.nombre in ['ficha_verificacion', 'supervisiones'] and informe.fecha_informe:
        mes_nombres = {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL',
            5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
            9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
        }
        mes_num = informe.fecha_informe.month
        mes_nombre = mes_nombres.get(mes_num, 'ENERO')
        path_parts.append(f'{mes_num:02d}-{mes_nombre}')
    elif informe.tipo.nombre == 'ias':
        path_parts.append('ANUAL')
    elif informe.tipo.nombre == 'its' and informe.informe_padre:
        if informe.informe_padre.trimestre:
            trimestre_map = {
                1: 'PRIMER_TRIMESTRE',
                2: 'SEGUNDO_TRIMESTRE',
                3: 'TERCER_TRIMESTRE',
                4: 'CUARTO_TRIMESTRE'
            }
            path_parts.append(trimestre_map.get(informe.informe_padre.trimestre, 'PRIMER_TRIMESTRE'))

    # Agregar carpeta de respuestas con el tipo de documento
    path_parts.append('RESPUESTAS')
    path_parts.append(tipo_documento.prefijo_carpeta)

    # Asegurar que el nombre del archivo tenga el formato correcto
    if not filename.startswith(f"RESP_{informe.tipo.nombre.upper()}_{informe.id}"):
        nombre_base, extension = os.path.splitext(filename)
        fecha_respuesta = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"RESP_{informe.tipo.nombre.upper()}_{informe.id}_{fecha_respuesta}_{nombre_base}{extension}"

    return os.path.join(*path_parts, filename)

# MODELO RespuestaInforme MODIFICADO
class RespuestaInforme(models.Model):
    informe = models.ForeignKey(Informe, on_delete=models.CASCADE, related_name='respuestas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_documento = models.ForeignKey(TipoDocumentoRespuesta, on_delete=models.CASCADE,
                                       help_text="Tipo de documento de respuesta")
    mensaje = models.TextField()
    archivo_adjunto = models.FileField(
        upload_to=upload_respuesta_to_structured_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx'])],
        null=True,
        blank=True,
        help_text="Archivo de respuesta (PDF, DOC, DOCX, XLS, XLSX)"
    )
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Respuesta de Informe"
        verbose_name_plural = "Respuestas de Informes"
        ordering = ['-fecha_respuesta']

    def __str__(self):
        return f"Respuesta de {self.usuario.get_full_name()} a {self.informe.titulo}"

    def get_archivo_nombre(self):
        """Devuelve solo el nombre del archivo sin la ruta"""
        if self.archivo_adjunto:
            return os.path.basename(self.archivo_adjunto.name)
        return None

    def get_info_origen(self):
        """Devuelve información del informe original para mostrar en la respuesta"""
        return {
            'municipalidad': self.informe.usuario.get_municipalidad_display(),
            'tipo_informe': self.informe.tipo.get_nombre_display(),
            'periodo': self.informe.get_periodo_display(),
            'titulo': self.informe.titulo,
            'id_informe': self.informe.id
        }

    def get_ruta_almacenamiento(self):
        """Devuelve la ruta donde se guardará el archivo"""
        if self.archivo_adjunto:
            return os.path.dirname(self.archivo_adjunto.name)
        return None