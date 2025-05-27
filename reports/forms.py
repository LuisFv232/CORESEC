from django import forms
from .models import Informe, TipoInforme, RespuestaInforme


class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['tipo', 'titulo', 'descripcion', 'año', 'trimestre', 'fecha_informe', 'informe_padre',
                  'archivo_adjunto']
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
                raise forms.ValidationError(
                    f'Los informes de {tipo.get_nombre_display()} requieren especificar una fecha.')

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
        fields = ['mensaje', 'archivo_adjunto']
        widgets = {
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
