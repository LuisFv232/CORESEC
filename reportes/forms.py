from django import forms
from django.db import models
from .models import Informe, TipoInforme, RespuestaInforme, TipoDocumentoRespuesta
from django.utils import timezone
import os


class TipoInformeForm(forms.ModelForm):
    class Meta:
        model = TipoInforme
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_display': forms.TextInput(attrs={'class': 'form-control'}),
            'estructura_carpetas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: INFORMES/{municipalidad}/{tipo}/{año}/{periodo}'
            }),
        }
        help_texts = {
            'estructura_carpetas': 'Variables disponibles: {municipalidad}, {tipo}, {año}, {periodo}'
        }


class TipoDocumentoRespuestaForm(forms.ModelForm):
    class Meta:
        model = TipoDocumentoRespuesta
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'prefijo_carpeta': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['tipo', 'titulo', 'descripcion', 'año', 'trimestre', 'fecha_informe', 'informe_padre',
                  'archivo_adjunto']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'onchange': 'actualizarCamposRequeridos()'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título descriptivo del informe',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del contenido del informe...',
                'required': True
            }),
            'año': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'trimestre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_informe': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'informe_padre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'archivo_adjunto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrar tipos de informe según el usuario
        if self.user:
            # Obtener todos los tipos activos que el usuario puede ver
            tipos_disponibles = TipoInforme.objects.filter(activo=True)

            # Filtrar por permisos del usuario
            if self.user.tipo_usuario == 'municipal':
                tipos_disponibles = tipos_disponibles.filter(permite_municipal=True)
            elif self.user.tipo_usuario == 'coordinador':
                tipos_disponibles = tipos_disponibles.filter(permite_coordinador=True)
            else:  # administrador
                tipos_disponibles = tipos_disponibles.filter(permite_admin=True)

            # Asignar el queryset filtrado
            self.fields['tipo'].queryset = tipos_disponibles

            # Configurar campos dinámicamente según el tipo seleccionado
            if 'tipo' in self.data:
                tipo_id = self.data.get('tipo')
                try:
                    tipo = TipoInforme.objects.get(id=tipo_id)
                    self.configurar_campos_por_tipo(tipo)
                except (ValueError, TypeError, TipoInforme.DoesNotExist):
                    pass
            elif self.instance.pk:
                self.configurar_campos_por_tipo(self.instance.tipo)

        # Configurar campos como opcionales inicialmente
        self.fields['trimestre'].required = False
        self.fields['fecha_informe'].required = False
        self.fields['informe_padre'].required = False
        self.fields['archivo_adjunto'].required = False

        # Mejorar la presentación del campo tipo
        self.fields['tipo'].empty_label = "Seleccione un tipo de informe"
        self.fields['tipo'].widget.attrs.update({
            'class': 'form-select select2',
            'data-placeholder': 'Seleccione un tipo de informe'
        })

    def configurar_campos_por_tipo(self, tipo):
        """Configura los campos según las necesidades del tipo de informe"""
        self.fields['trimestre'].required = tipo.requiere_trimestre
        self.fields['fecha_informe'].required = tipo.requiere_fecha
        self.fields['informe_padre'].required = tipo.requiere_informe_padre
        self.fields['archivo_adjunto'].required = tipo.permite_adjuntos

        # Ocultar campos no requeridos
        self.fields['trimestre'].widget.attrs['style'] = 'display:none;' if not tipo.requiere_trimestre else ''
        self.fields['fecha_informe'].widget.attrs['style'] = 'display:none;' if not tipo.requiere_fecha else ''
        self.fields['informe_padre'].widget.attrs['style'] = 'display:none;' if not tipo.requiere_informe_padre else ''

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')

        if tipo:
            if tipo.requiere_trimestre and not cleaned_data.get('trimestre'):
                self.add_error('trimestre', 'Este tipo de informe requiere especificar el trimestre.')
            if tipo.requiere_fecha and not cleaned_data.get('fecha_informe'):
                self.add_error('fecha_informe', 'Este tipo de informe requiere especificar una fecha.')
            if tipo.requiere_informe_padre and not cleaned_data.get('informe_padre'):
                self.add_error('informe_padre', 'Este tipo de informe requiere un informe padre específico.')

        return cleaned_data


class RespuestaInformeForm(forms.ModelForm):
    class Meta:
        model = RespuestaInforme
        fields = ['tipo_documento', 'mensaje', 'archivo_adjunto']
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escribe tu respuesta o comentarios sobre el informe...',
                'required': True
            }),
            'archivo_adjunto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx'
            })
        }

    def __init__(self, *args, **kwargs):
        informe = kwargs.pop('informe', None)
        super().__init__(*args, **kwargs)

        # Filtrar solo tipos de documento activos y permitidos para el usuario
        if informe and hasattr(informe, 'usuario'):
            self.fields['tipo_documento'].queryset = TipoDocumentoRespuesta.objects.filter(
                activo=True
            ).filter(
                models.Q(permite_municipal=True) if informe.usuario.tipo_usuario == 'municipal' else
                models.Q(permite_coordinador=True) if informe.usuario.tipo_usuario == 'coordinador' else
                models.Q(permite_admin=True)
            )

        # Personalizar el label del tipo de documento
        self.fields['tipo_documento'].label = 'Tipo de Documento de Respuesta'
        self.fields['tipo_documento'].help_text = 'Selecciona el tipo de documento que vas a adjuntar como respuesta'

        # Hacer archivo adjunto requerido solo si se selecciona un tipo de documento
        self.fields['archivo_adjunto'].required = False

        # Si tenemos el informe, podemos personalizar más cosas
        if informe:
            self.informe = informe

    def clean(self):
        cleaned_data = super().clean()
        tipo_documento = cleaned_data.get('tipo_documento')
        archivo_adjunto = cleaned_data.get('archivo_adjunto')
        mensaje = cleaned_data.get('mensaje')

        # Validar que al menos haya mensaje
        if not mensaje or not mensaje.strip():
            raise forms.ValidationError('Debe proporcionar un mensaje de respuesta.')

        # Si se selecciona un tipo de documento, debe haber archivo
        if tipo_documento and not archivo_adjunto:
            raise forms.ValidationError(f'Debe adjuntar un archivo del tipo: {tipo_documento.get_nombre_display()}')

        return cleaned_data