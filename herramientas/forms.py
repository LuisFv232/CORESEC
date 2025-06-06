from django import forms
from .models import Documento, Enlace, TipoDocumento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'tipo', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del documento'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del documento'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx'
            })
        }

class EnlaceForm(forms.ModelForm):
    class Meta:
        model = Enlace
        fields = ['titulo', 'descripcion', 'url', 'categoria']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del enlace'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del enlace'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            })
        }

class TipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prefijo_carpeta': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'prefijo_carpeta': 'Prefijo para la estructura de carpetas (ej: INF, FIC, SUP)',
        }