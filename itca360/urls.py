from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.shortcuts import render

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    else:
        # Aquí puedes pasar estadísticas públicas
        from usuarios.models import Usuario
        from reportes.models import Informe
        context = {
            'total_usuarios': Usuario.objects.count(),
            'total_informes': Informe.objects.count(),
            'total_municipalidades': 11,
        }
        return render(request, 'home/landing.html', context)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('usuarios/', include('usuarios.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('reportes/', include('reportes.urls')),
    path('notificaciones/', include('notificaciones.urls')),
    path('herramientas/', include('herramientas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
