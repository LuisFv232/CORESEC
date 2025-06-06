from django.contrib import admin
from .models import Report, ReportAnalysis, Observation

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'municipality', 'status', 'upload_date')
    list_filter = ('status', 'municipality', 'upload_date')
    search_fields = ('title', 'uploaded_by__email', 'municipality')

@admin.register(ReportAnalysis)
class ReportAnalysisAdmin(admin.ModelAdmin):
    list_display = ('report', 'analyzed_date', 'structure_valid', 'content_valid')
    list_filter = ('structure_valid', 'content_valid', 'analyzed_date')

@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'severity', 'sheet_name', 'description')
    list_filter = ('severity', 'sheet_name')
