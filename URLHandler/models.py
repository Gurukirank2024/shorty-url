from django.db import models
from django.conf import settings   # use AUTH_USER_MODEL

class ShortURL(models.Model):   # <-- capitalized class name
    originalURL = models.URLField(blank=False)
    shortQuery = models.CharField(blank=False, max_length=8, unique=True)
    visits = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="short_urls")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shortQuery} -> {self.originalURL}"


# ✅ New model for analytics
class ClickEvent(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE, related_name="click_events")
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click on {self.short_url.shortQuery} at {self.clicked_at}"