from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)   # email must be unique
    username = models.CharField(max_length=150, unique=False)  # allow duplicate usernames

    USERNAME_FIELD = 'email'   # login with email instead of username
    REQUIRED_FIELDS = ['username']   # username is still required but not unique
