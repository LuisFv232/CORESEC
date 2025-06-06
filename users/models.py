from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('COORDINATOR', 'Coordinador'),
        ('MUNICIPAL_MANAGER', 'Encargado Municipal'),
    )
    
    MUNICIPALITY_CHOICES = (
        ('HUANUCO', 'Huánuco'),
        ('AMBO', 'Ambo'),
        ('DOS_DE_MAYO', 'Dos de Mayo'),
        ('HUACAYBAMBA', 'Huacaybamba'),
        ('HUAMALIES', 'Huamalíes'),
        ('LEONCIO_PRADO', 'Leoncio Prado'),
        ('MARAÑON', 'Marañón'),
        ('PACHITEA', 'Pachitea'),
        ('PUERTO_INCA', 'Puerto Inca'),
        ('LAURICOCHA', 'Lauricocha'),
        ('YAROWILCA', 'Yarowilca'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MUNICIPAL_MANAGER', verbose_name="Tipo de Usuario")
    municipality = models.CharField(max_length=100, choices=MUNICIPALITY_CHOICES, blank=True, null=True, verbose_name="Municipalidad")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cargo")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Número de Celular")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
