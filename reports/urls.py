from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('upload/', views.upload_report, name='upload_report'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    path('<int:report_id>/analysis/', views.report_analysis, name='report_analysis'),
]
