from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ShortURL

@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ("shortQuery", "originalURL", "visits", "user", "created_at")
    search_fields = ("shortQuery", "originalURL")
    list_filter = ("created_at", "user")

