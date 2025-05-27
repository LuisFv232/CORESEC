from django.db import models
from django.conf import settings

class Report(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('ANALYZING', 'Analizando'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
    )
    
    REPORT_TYPE_CHOICES = (
        ('ITCA', 'Informe Trimestral de Actividades ITCA'),
        ('TRIMESTRAL_SEGUIMIENTO', 'Informe Trimestral de Seguimiento'),
        ('ANUAL_SEGUIMIENTO', 'Informe Anual de Seguimiento'),
        ('SUPERVISION', 'Supervisión'),
        ('FICHA_VERIFICACION', 'Ficha de Verificación'),
    )
    
    TRIMESTER_CHOICES = (
        ('Q1', 'Primer Trimestre (Ene-Mar)'),
        ('Q2', 'Segundo Trimestre (Abr-Jun)'),
        ('Q3', 'Tercer Trimestre (Jul-Sep)'),
        ('Q4', 'Cuarto Trimestre (Oct-Dic)'),
    )
    
    YEAR_CHOICES = [(str(year), str(year)) for year in range(2020, 2031)]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES, verbose_name="Tipo de Informe")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    year = models.CharField(max_length=4, choices=YEAR_CHOICES, verbose_name="Año")
    trimester = models.CharField(max_length=2, choices=TRIMESTER_CHOICES, blank=True, null=True, verbose_name="Trimestre")
    
    # Archivos (hasta 4)
    file1 = models.FileField(upload_to='reports/', verbose_name="Archivo 1")
    file2 = models.FileField(upload_to='reports/', blank=True, null=True, verbose_name="Archivo 2 (opcional)")
    file3 = models.FileField(upload_to='reports/', blank=True, null=True, verbose_name="Archivo 3 (opcional)")
    file4 = models.FileField(upload_to='reports/', blank=True, null=True, verbose_name="Archivo 4 (opcional)")
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    municipality = models.CharField(max_length=100, verbose_name="Municipalidad")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Última Modificación")
    
    def __str__(self):
        return self.title
    
    def get_main_file(self):
        return self.file1
    
    def has_additional_files(self):
        return self.file2 or self.file3 or self.file4
    
    def get_additional_files(self):
        files = []
        if self.file2:
            files.append(('Archivo 2', self.file2))
        if self.file3:
            files.append(('Archivo 3', self.file3))
        if self.file4:
            files.append(('Archivo 4', self.file4))
        return files
    
    def needs_trimester(self):
        return self.report_type in ['ITCA', 'TRIMESTRAL_SEGUIMIENTO', 'SUPERVISION', 'FICHA_VERIFICACION']

class ReportAnalysis(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='analysis')
    analyzed_date = models.DateTimeField(auto_now_add=True)
    structure_valid = models.BooleanField(default=False)
    content_valid = models.BooleanField(default=False)
    summary = models.TextField()
    
    def __str__(self):
        return f"Análisis de {self.report.title}"

class Observation(models.Model):
    SEVERITY_CHOICES = (
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('CRITICAL', 'Crítica'),
    )
    
    analysis = models.ForeignKey(ReportAnalysis, on_delete=models.CASCADE, related_name='observations')
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    sheet_name = models.CharField(max_length=100)
    cell_reference = models.CharField(max_length=20, blank=True, null=True)
    recommendation = models.TextField()
    
    def __str__(self):
        return f"{self.get_severity_display()}: {self.description[:50]}"
