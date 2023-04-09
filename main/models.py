from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Destination(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    popular = models.BooleanField(default=False)

class User(AbstractUser):
    destinations = models.ManyToManyField(Destination, related_name="booker", blank=True)
