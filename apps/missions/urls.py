from django.urls import path
from . import views

app_name = 'missions'

urlpatterns = [
    path('', views.mission_list, name='list'),
    path('detail/<int:mission_id>/', views.mission_detail_page, name='detail'),
    path('favorite/add/', views.add_favorite, name='add_favorite'),
    path('favorite/remove/<int:pk>/', views.remove_favorite, name='remove_favorite'),
    path('api/list/', views.api_missions, name='api_list'),
    path('api/detail/<int:mission_id>/', views.api_mission_detail, name='api_detail'),
]
