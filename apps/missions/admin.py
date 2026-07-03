from django.contrib import admin
from .models import FavoriteMission


@admin.register(FavoriteMission)
class FavoriteMissionAdmin(admin.ModelAdmin):
    list_display = ('mission_name', 'created_at')
