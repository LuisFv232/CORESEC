from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from reportes.models import Informe, TipoInforme
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class InformesTestCase(TestCase):
    def setUp(self):
        # Crear usuarios de prueba
        self.admin = User.objects.create_user(
            username='admin_test',
            password='test123',
            tipo_usuario='administrador',
            cargo_coresec='director_ejecutivo'
        )
        
        self.municipal = User.objects.create_user(
            username='municipal_test',
            password='test123',
            tipo_usuario='municipal',
            municipalidad='huanuco',
            cargo_municipal='alcalde'
        )
        
        # Crear tipo de informe
        self.tipo_informe = TipoInforme.objects.create(
            nombre='itca_trimestral',
            descripcion='Test ITCA',
            categoria='itca',
            requiere_periodo=True
        )
        
        self.client = Client()

    def test_crear_informe_municipal(self):
        """Test que usuario municipal puede crear informe"""
        self.client.login(username='municipal_test', password='test123')
        
        # Crear archivo de prueba
        archivo = SimpleUploadedFile("test.pdf", b"contenido de prueba", content_type="application/pdf")
        
        response = self.client.post('/reportes/crear/', {
            'tipo': self.tipo_informe.id,
            'titulo': 'Informe de Prueba',
            'descripcion': 'Descripción de prueba',
            'año': '2024',
            'trimestre': '1',
            'archivo_adjunto': archivo
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect después de crear
        self.assertTrue(Informe.objects.filter(titulo='Informe de Prueba').exists())

    def test_admin_puede_ver_todos_informes(self):
        """Test que administrador puede ver todos los informes"""
        # Crear informe
        informe = Informe.objects.create(
            usuario=self.municipal,
            tipo=self.tipo_informe,
            titulo='Informe Municipal',
            descripcion='Test',
            año='2024',
            trimestre='1'
        )
        
        self.client.login(username='admin_test', password='test123')
        response = self.client.get('/reportes/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informe Municipal')

    def test_municipal_solo_ve_sus_informes(self):
        """Test que usuario municipal solo ve sus propios informes"""
        # Crear otro usuario municipal
        otro_municipal = User.objects.create_user(
            username='otro_municipal',
            password='test123',
            tipo_usuario='municipal',
            municipalidad='ambo'
        )
        
        # Crear informes de ambos usuarios
        informe_propio = Informe.objects.create(
            usuario=self.municipal,
            tipo=self.tipo_informe,
            titulo='Mi Informe',
            descripcion='Test',
            año='2024'
        )
        
        informe_ajeno = Informe.objects.create(
            usuario=otro_municipal,
            tipo=self.tipo_informe,
            titulo='Informe Ajeno',
            descripcion='Test',
            año='2024'
        )
        
        self.client.login(username='municipal_test', password='test123')
        response = self.client.get('/reportes/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mi Informe')
        self.assertNotContains(response, 'Informe Ajeno')
