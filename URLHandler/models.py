from django.db import models
from django.conf import settings   # use AUTH_USER_MODEL

class ShortURL(models.Model):   # <-- capitalized class name
    originalURL = models.URLField(blank=False)
    shortQuery = models.CharField(blank=False, max_length=8)
    visits = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shortQuery} -> {self.originalURL}"
