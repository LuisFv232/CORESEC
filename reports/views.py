from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Report
from .forms import ReportUploadForm

@login_required
def report_list(request):
    user = request.user
    
    # Filtrar informes según el rol del usuario
    if user.role == 'ADMIN' or user.role == 'COORDINATOR':
        reports = Report.objects.all().order_by('-upload_date')
    else:
        reports = Report.objects.filter(uploaded_by=user).order_by('-upload_date')
    
    return render(request, 'reports/report_list.html', {'reports': reports})

@login_required
def upload_report(request):
    if request.method == 'POST':
        form = ReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.uploaded_by = request.user
            
            # Si es encargado municipal, usar su municipalidad
            if request.user.role == 'MUNICIPAL_MANAGER' and request.user.municipality:
                report.municipality = request.user.municipality
                
            report.save()
            messages.success(request, 'Informe subido correctamente.')
            return redirect('report_list')
    else:
        initial_data = {}
        
        # Pre-seleccionar municipalidad si es encargado municipal
        if request.user.role == 'MUNICIPAL_MANAGER' and request.user.municipality:
            initial_data['municipality'] = request.user.municipality
            
        form = ReportUploadForm(initial=initial_data)
        
        # Hacer el campo de municipalidad de solo lectura para encargados municipales
        if request.user.role == 'MUNICIPAL_MANAGER':
            form.fields['municipality'].widget.attrs['disabled'] = 'disabled'
    
    return render(request, 'reports/upload_report.html', {'form': form})

@login_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    # Verificar permisos
    if request.user.role == 'MUNICIPAL_MANAGER' and report.uploaded_by != request.user:
        messages.error(request, 'No tienes permisos para ver este informe.')
        return redirect('report_list')
    
    return render(request, 'reports/report_detail.html', {'report': report})

@login_required
def report_analysis(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    # Solo administradores y coordinadores pueden ver análisis
    if request.user.role == 'MUNICIPAL_MANAGER':
        messages.error(request, 'No tienes permisos para ver el análisis.')
        return redirect('report_detail', report_id=report_id)
    
    analysis = getattr(report, 'analysis', None)
    return render(request, 'reports/report_analysis.html', {'report': report, 'analysis': analysis})
