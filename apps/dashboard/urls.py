from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('bookmark/add/', views.add_bookmark, name='add_bookmark'),
    path('bookmark/remove/<int:pk>/', views.remove_bookmark, name='remove_bookmark'),
    path('api/stats/', views.api_dashboard_stats, name='api_stats'),
    path('api/charts/', views.api_dashboard_charts, name='api_charts'),
    path('api/insights/', views.api_insights, name='api_insights'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/suggestions/', views.api_search_suggestions, name='api_suggestions'),
    path('api/filters/', views.api_filter_options, name='api_filters'),
    path('api/metadata/', views.api_metadata, name='api_metadata'),
]
