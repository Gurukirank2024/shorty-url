from django.contrib.auth.models import AbstractUser
from django.db import models

# -------------------------------
# Custom User Model
# -------------------------------
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)   # email must be unique
    username = models.CharField(max_length=150, unique=False)  # allow duplicate usernames

    USERNAME_FIELD = 'email'   # login with email instead of username
    REQUIRED_FIELDS = ['username']   # username is still required but not unique

    def __str__(self):
        return self.email

# -------------------------------
# Shortened URL Model
# -------------------------------
class ShortURL(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    originalURL = models.URLField()
    shortQuery = models.CharField(max_length=20, unique=True)
    visits = models.PositiveIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_clicked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.shortQuery} -> {self.originalURL}"

# -------------------------------
# Click Event Model (for analytics)
# -------------------------------
class ClickEvent(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click on {self.short_url.shortQuery} at {self.clicked_at}"