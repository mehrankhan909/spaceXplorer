from django.contrib import admin
from .models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('mission_name', 'created_at')
    search_fields = ('mission_name',)
