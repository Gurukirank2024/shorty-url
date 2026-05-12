from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ShortURL
from .models import ShortURL, ClickEvent

@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ("shortQuery", "originalURL", "visits", "user", "created_at")
    search_fields = ("shortQuery", "originalURL")
    list_filter = ("created_at", "user")

@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ("short_url", "ip_address", "country", "referrer", "clicked_at")
    search_fields = ("ip_address", "country", "referrer")
    list_filter = ("country", "clicked_at")


