from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu apellido'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '999-999-999'
        })
    )
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingresa tu dirección completa'
        })
    )
    tipo_usuario = forms.ChoiceField(
        choices=Usuario.TIPO_USUARIO_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    municipalidad = forms.ChoiceField(
        choices=[('', 'Selecciona municipalidad...')] + Usuario.MUNICIPALIDADES_HUANUCO,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    cargo_coresec = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Director Ejecutivo, Coordinador General, etc.'
        })
    )
    cargo_municipal = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Alcalde, Gerente Municipal, etc.'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 
                 'telefono', 'direccion', 'tipo_usuario', 'municipalidad', 'cargo_coresec', 'cargo_municipal')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        municipalidad = cleaned_data.get('municipalidad')
        cargo_coresec = cleaned_data.get('cargo_coresec')
        cargo_municipal = cleaned_data.get('cargo_municipal')
        
        if tipo_usuario == 'municipal':
            if not municipalidad:
                raise forms.ValidationError('Debes seleccionar una municipalidad.')
            if not cargo_municipal or not cargo_municipal.strip():
                raise forms.ValidationError('Debes especificar tu cargo municipal.')
        elif tipo_usuario in ['administrador', 'coordinador']:
            if not cargo_coresec or not cargo_coresec.strip():
                raise forms.ValidationError('Debes especificar tu cargo en CORESEC.')
        
        return cleaned_data

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'direccion', 'tipo_usuario', 
                 'municipalidad', 'cargo_coresec', 'cargo_municipal']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'municipalidad': forms.Select(attrs={'class': 'form-select'}),
            'cargo_coresec': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifica tu cargo en CORESEC'}),
            'cargo_municipal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifica tu cargo municipal'}),
        }

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'direccion', 
                 'tipo_usuario', 'municipalidad', 'cargo_coresec', 'cargo_municipal', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'municipalidad': forms.Select(attrs={'class': 'form-select'}),
            'cargo_coresec': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_municipal': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CrearUsuarioForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    tipo_usuario = forms.ChoiceField(choices=Usuario.TIPO_USUARIO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    municipalidad = forms.ChoiceField(choices=[('', 'Seleccionar...')] + Usuario.MUNICIPALIDADES_HUANUCO, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    cargo_coresec = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifica tu cargo en CORESEC'}))
    cargo_municipal = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifica tu cargo municipal'}))
    
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',
                 'telefono', 'direccion', 'tipo_usuario', 'municipalidad', 'cargo_coresec', 'cargo_municipal')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
