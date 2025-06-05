from django import forms
from django.utils import timezone
from .models import Informe, TipoInforme, RespuestaInforme, TipoDocumentoRespuesta
import os

class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['tipo', 'titulo', 'descripcion', 'año', 'trimestre', 'fecha_informe', 'informe_padre', 'archivo_adjunto']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
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
                'accept': '.pdf,.doc,.docx,.xls,.xlsx',
                'required': True
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrar tipos de informe según el usuario
        if user:
            tipos_disponibles = []
            for tipo in TipoInforme.objects.filter(activo=True):
                if tipo.puede_acceder(user.tipo_usuario):
                    tipos_disponibles.append(tipo.id)

            self.fields['tipo'].queryset = TipoInforme.objects.filter(id__in=tipos_disponibles)

            # Para ITS, solo mostrar informes ITCA del usuario como opciones padre
            if user.tipo_usuario in ['administrador', 'coordinador']:
                informes_itca = Informe.objects.filter(
                    tipo__nombre='itca',
                    estado__in=['pendiente', 'en_revision']
                )
                self.fields['informe_padre'].queryset = informes_itca
            else:
                self.fields['informe_padre'].queryset = Informe.objects.none()
        else:
            # Si no hay usuario, mostrar todos los tipos activos
            self.fields['tipo'].queryset = TipoInforme.objects.filter(activo=True)

        # Configurar campos como opcionales inicialmente
        self.fields['trimestre'].required = False
        self.fields['fecha_informe'].required = False
        self.fields['informe_padre'].required = False

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        trimestre = cleaned_data.get('trimestre')
        fecha_informe = cleaned_data.get('fecha_informe')
        informe_padre = cleaned_data.get('informe_padre')

        if tipo:
            # Validar ITCA - requiere trimestre y año
            if tipo.nombre == 'itca' and not trimestre:
                raise forms.ValidationError('Los informes ITCA requieren especificar el trimestre.')

            # Validar Ficha de Verificación y Supervisiones - requieren fecha
            if tipo.nombre in ['ficha_verificacion', 'supervisiones'] and not fecha_informe:
                raise forms.ValidationError(f'Los informes de {tipo.get_nombre_display()} requieren especificar una fecha.')

            # Validar ITS - requiere informe padre ITCA
            if tipo.nombre == 'its' and not informe_padre:
                raise forms.ValidationError('Los informes ITS deben responder a un informe ITCA específico.')

            # Validar que IAS no requiere trimestre
            if tipo.nombre == 'ias' and trimestre:
                cleaned_data['trimestre'] = None  # Limpiar trimestre para IAS

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

        # Filtrar solo tipos de documento activos
        self.fields['tipo_documento'].queryset = TipoDocumentoRespuesta.objects.filter(activo=True)

        # Personalizar el label del tipo de documento
        self.fields['tipo_documento'].label = 'Tipo de Documento de Respuesta'
        self.fields['tipo_documento'].help_text = 'Selecciona el tipo de documento que vas a adjuntar como respuesta'

        # Hacer archivo adjunto requerido solo si se selecciona un tipo de documento
        self.fields['archivo_adjunto'].required = False

        # Si tenemos el informe, podemos personalizar más cosas
        if informe:
            self.informe = informe
            # Establecer el nombre del archivo sugerido
            fecha_actual = timezone.now().strftime('%Y%m%d')
            self.fields['archivo_adjunto'].widget.attrs['data-suggested-name'] = (
                f"RESP_{informe.tipo.nombre.upper()}_{informe.id}_{fecha_actual}"
            )

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