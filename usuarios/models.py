from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('administrador', 'Administrador CORESEC'),
        ('coordinador', 'Coordinador CORESEC'),
        ('municipal', 'Encargado Municipal'),
    ]
    
    MUNICIPALIDADES_HUANUCO = [
        ('huamalies', 'Huamalíes'),
        ('huacaybamba', 'Huacaybamba'),
        ('leoncio_prado', 'Leoncio Prado'),
        ('yarowilca', 'Yarowilca'),
        ('pachitea', 'Pachitea'),
        ('maranon', 'Marañón'),
        ('ambo', 'Ambo'),
        ('lauricocha', 'Lauricocha'),
        ('huanuco', 'Huánuco'),
        ('puerto_inca', 'Puerto Inca'),
        ('dos_de_mayo', 'Dos de Mayo'),
    ]
    
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='municipal')
    municipalidad = models.CharField(max_length=50, choices=MUNICIPALIDADES_HUANUCO, blank=True, null=True)
    cargo_coresec = models.CharField(max_length=100, blank=True, null=True, help_text="Especifica tu cargo en CORESEC")
    cargo_municipal = models.CharField(max_length=100, blank=True, null=True, help_text="Especifica tu cargo municipal")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_tipo_usuario_display()})"
    
    def get_cargo_display(self):
        if self.tipo_usuario in ['administrador', 'coordinador']:
            return self.cargo_coresec if self.cargo_coresec else 'Sin cargo asignado'
        else:
            return self.cargo_municipal if self.cargo_municipal else 'Sin cargo asignado'
    
    def get_municipalidad_display(self):
        if self.municipalidad:
            return dict(self.MUNICIPALIDADES_HUANUCO)[self.municipalidad]
        return 'Sin municipalidad asignada'
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
