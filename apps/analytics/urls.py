from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_page, name='page'),
    path('drilldown/<str:chart_id>/', views.drilldown_page, name='drilldown'),
    path('api/all/', views.api_all_charts, name='api_all'),
    path('api/<str:chart_id>/', views.api_chart_data, name='api_chart'),
    path('api/<str:chart_id>/missions/', views.api_drilldown_missions, name='api_drilldown'),
]
