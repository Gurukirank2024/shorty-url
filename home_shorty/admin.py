from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import short_url

@admin.register(short_url)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ("short_Query", "original_URL")
    search_fields = ("short_Query", "original_URL")

