from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_page, name='page'),
    path('statistics/', views.statistics_page, name='statistics'),
    path('data-quality/', views.data_quality_page, name='data_quality'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('api/summary/', views.api_report_summary, name='api_summary'),
    path('api/statistics/', views.api_statistics, name='api_statistics'),
    path('api/quality/', views.api_data_quality, name='api_quality'),
]
