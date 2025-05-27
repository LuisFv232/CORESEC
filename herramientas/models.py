from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Documento(models.Model):
    TIPO_CHOICES = [
        ('manual', 'Manual'),
        ('guia', 'Guía'),
        ('formato', 'Formato'),
        ('directiva', 'Directiva'),
        ('resolucion', 'Resolución'),
        ('otro', 'Otro'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    archivo = models.FileField(upload_to='documentos/')
    usuario_subida = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return self.titulo


class Enlace(models.Model):
    CATEGORIA_CHOICES = [
        ('institucional', 'Institucional'),
        ('academico', 'Académico'),
        ('soporte', 'Soporte'),
        ('normativo', 'Normativo'),
        ('capacitacion', 'Capacitación'),
        ('herramienta', 'Herramienta'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    url = models.URLField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    icono = models.CharField(max_length=50, default='fas fa-link')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # NUEVO CAMPO
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Enlace"
        verbose_name_plural = "Enlaces"
        ordering = ['categoria', 'titulo']

    def __str__(self):
        return self.titulo

class RecursoConasec(models.Model):
    """Recursos extraídos de la página de CONASEC"""
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    url = models.URLField()
    categoria = models.CharField(max_length=100)
    tipo_archivo = models.CharField(max_length=10, blank=True)  # PDF, DOC, etc.
    tamaño_archivo = models.CharField(max_length=20, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Recurso CONASEC"
        verbose_name_plural = "Recursos CONASEC"
        ordering = ['categoria', 'titulo']
    
    def __str__(self):
        return self.titulo
